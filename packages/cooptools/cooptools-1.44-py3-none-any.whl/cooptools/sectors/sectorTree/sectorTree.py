from cooptools.sectors import RectGrid
from cooptools.geometry_utils import rect_utils as rect
from cooptools.geometry_utils import vector_utils as vec
from typing import Dict, Any, Tuple, List, Callable
import cooptools.sectors.sect_utils as sec_u
from cooptools.coopEnum import CardinalPosition
import logging
import matplotlib.patches as patches
from cooptools.colors import Color
from cooptools.plotting import plot_series

class SectorTree:
    def __init__(self,
                 area_rect: rect.Rect,
                 capacity: int,
                 shape: Tuple[int, int],
                 parent=None, lvl:int = None,
                 max_lvls: int = None):
        self.parent = parent
        self.children = {}
        self.capacity = capacity
        self.grid = RectGrid(shape[0], shape[1])
        self._area = area_rect
        self._client_mapping = {}
        self._last_mapped_pos = {}
        self.lvl = lvl if lvl else 0
        self.max_lvls = max_lvls

    def __str__(self):
        return f"{self.grid}, \n{self.children}"

    def _add_child_layer(self, grid_pos: Tuple[int, int]):
        # get the bottom left coord of the grid pos
        grid_pos_bl_coord = sec_u.coord_of_sector(area_dims=(self._area[2], self._area[3]),
                                                  sector_def=self.grid.Shape,
                                                  sector=grid_pos,
                                                  cardinality=CardinalPosition.BOTTOM_LEFT)

        # define the area rectangle that will encompass the new child layer
        child_rect = (
            grid_pos_bl_coord[0] + self._area[0],
            grid_pos_bl_coord[1] + self._area[1],
            self._area[2] / self.grid.nColumns,
            self._area[3] / self.grid.nRows
        )

        # add a new SectorTree as a child to the grid pos
        self.children[grid_pos] = SectorTree(area_rect=child_rect,
                                             capacity=self.capacity,
                                             shape=self.grid.Shape,
                                             parent=self,
                                             lvl=self.lvl+1,
                                             max_lvls=self.max_lvls)

        # update clients in child at grid pos. This should happen whenever you add a child. it should iterate the
        # clients at the grid pos and add them to the child layer appropriately
        clients = self._client_mapping.get(grid_pos, None)
        for client in clients:
            self.children[grid_pos].add_update_clients(client, self._last_mapped_pos[client])

        logging.info(f"child layer added at {self.lvl}: {grid_pos} with area rect: {child_rect}")

    def _handle_child_layer(self, grid_pos: Tuple[int, int]):

        # capacity has not been reached (mult clients at shared pos are treated as 1). Therefore, we choose not
        # to add a child (or handle). We can return early bc there is not a reason to handle children in this case.
        # Additionally, we do not want to continue if we have reached our max-level depth
        clients = self._client_mapping.get(grid_pos, None)
        positions = set([self._last_mapped_pos[client] for client in clients])
        if clients is None \
                or len(positions) <= self.capacity \
                or (self.max_lvls is not None and self.lvl >= self.max_lvls - 1):
            return False

        # there is no child but capacity is reached. we need to add a child layer to the tree
        if self.children.get(grid_pos, None) is None and len(positions) > self.capacity:
            self._add_child_layer(grid_pos)
        return True

    def add_update_client(self, client, pos: Tuple[float, float]):
        if self.lvl == 0:
            logging.info(f"User requests adding [{client}] to {pos}")

        if not client.__hash__:
            raise Exception(f"Client {client} must be hashable, but type {type(client)} is not")

        # check if can skip since already up to date
        last_pos = self._last_mapped_pos.get(client, None)
        if last_pos is not None and last_pos == pos:
            logging.info(f"no change: client [{client}] already exists at {self.lvl}: {last_pos}")
            return

        # check if already have client in but at a different location
        if last_pos is not None and last_pos != pos:
            logging.info(f"conflict: client [{client}] already exists at {self.lvl}: {last_pos}")
            self.remove_client(client)


        # Check for client position in the lvl
        pos_in_lvl = pos[0] - self._area[0], pos[1] - self._area[1]

        # obtain the grid pos that the pos lands in in the lvl
        grid_pos = sec_u.sector_from_coord(coord=pos_in_lvl,
                                           area_dims=(self._area[2], self._area[3]),
                                           sector_def=self.grid.Shape)

        # if grid_pos is None, the pos is not in the boundary
        if grid_pos is None:
            raise ValueError(f"The provided pos {pos} does not fall in the boundary of the area: {self._area}")

        # add/update the mappings
        self._client_mapping.setdefault(grid_pos, set()).add(client)
        self._last_mapped_pos[client] = pos
        logging.info(f"client [{client}] added to {self.lvl}: {grid_pos} at {pos}")


        # handle child lvl
        layer_added = self._handle_child_layer(grid_pos)

        if self.children.get(grid_pos, None) is not None:
            self.children[grid_pos].add_update_clients(client, self._last_mapped_pos[client])

    def remove_client(self, client):
        # if not a member, early out
        if client not in self._last_mapped_pos.keys():
            return

        logging.info(f"removing client [{client}] from {self.lvl}: {self._last_mapped_pos[client]}")

        # delete from last mapped
        del self._last_mapped_pos[client]

        # delete from client mappings
        for grid_pos, clients in self._client_mapping.items():
            if client in clients:
                clients.remove(client)

        # handle children
        to_remove = []
        for pos, child in self.children.items():
            # remove client from child
            child.remove_clients(client)

            #remove child if empty
            positions = set([pos for client, pos in child.ClientsPos.items()])
            if len(positions) <= self.capacity:
                to_remove.append(pos)

        for child in to_remove:
            del self.children[child]

    def _sector_corners_nearby(self, radius: float, pt: Tuple[float, float]):
        ret = {}
        for pos, sector in self.MySectors:
            corners = rect.rect_corners(sector)

            tl = self._within_radius_of_point(corners[CardinalPosition.TOP_LEFT], radius=radius, pt=pt)
            tr = self._within_radius_of_point(corners[CardinalPosition.TOP_RIGHT], radius, pt)
            bl = self._within_radius_of_point(corners[CardinalPosition.BOTTOM_LEFT], radius, pt)
            br = self._within_radius_of_point(corners[CardinalPosition.BOTTOM_RIGHT], radius, pt)
            ret[pos] = sum([tl, tr, bl, br])

        return ret

    def _sectors_potentially_overlaps_radius(self, radius: float, pt: Tuple[float, float]):
        ret = {}
        for pos, sector_area in self.MySectors:
            ret[pos] = False

            # determine if the bounding circle of my area plus the radius given to check is more than the distance
            # between the center of my area and the point to be checked. If the combined distance of the two radius's is
            # smaller than the distance between center and pt, we can safely assume that the area of the sector does NOT
            # intersect with the area being checked. However if it is larger, there is a potential that the area falls
            # within the checked area
            if rect.bounding_circle_radius(sector_area) + radius >= vec.distance_between(pt, rect.rect_center(sector_area)):
                ret[pos] = True
        return ret


    def nearby_clients(self, radius: float, pt: Tuple[float, float]) -> Dict[Any, Tuple[float, float]]:
        sectors_nearby = self._sectors_potentially_overlaps_radius(radius, pt)
        corners_nearby = self._sector_corners_nearby(radius, pt)

        clients = {}
        for sector, nearby in sectors_nearby.items():
            # if sector is not nearby, continue
            if not nearby:
                continue

            # if sector is determined to be nearby, check if all 4 corners are nearby. If so, easily assume that all
            # its member clients are also nearby and early out.
            # For case when it is nearby, but no clients, also early out
            if corners_nearby[sector] == 4 and self._client_mapping.get(sector, None) is not None:
                sec_clients = self._client_mapping.get(sector, [])
                clients.update({client: self._last_mapped_pos[client] for client in sec_clients})
                continue

            # if there is a child, find nearby in child
            if self.children.get(sector, None) is not None:
                nearby_in_child = self.children[sector].nearby_clients(radius, pt)
                clients.update(nearby_in_child)
            # sector is nearby, no child but there are mapped clients
            elif self._client_mapping.get(sector, None) is not None:
                nearby_in_sector = self._nearby_in_my_sector(sector, radius, pt)
                clients.update(nearby_in_sector)

        return clients

    def _nearby_in_my_sector(self,
                             sector: Tuple[int, int],
                             radius: float,
                             pt: Tuple[float, float]) -> Dict[Any, Tuple[float, float]]:
        # collect clients in sector
        # sector_clients = list(self._client_mapping[sector])
        nearby_in_sector = {client: self._last_mapped_pos[client] for client in self._client_mapping[sector]}

        # prune clients in sector that arent actually nearby by enumerating against the convex_qualifier
        to_prune = []
        for client, pos in nearby_in_sector.items():
            if not self._within_radius_of_point(pos, radius, pt):
                to_prune.append(client)

        for client in to_prune:
            del nearby_in_sector[client]

        # return
        return nearby_in_sector

    def _within_radius_of_point(self, check: Tuple[float, float], radius: float, pt: Tuple[float, float]):
        return vec.distance_between(check, pt) <= radius

    @property
    def ClientMappings(self) -> Dict[Tuple[int, int], set[Any]]:
        return self._client_mapping

    @property
    def ClientsPos(self) -> Dict[Any, Tuple[float, float]]:
        return self._last_mapped_pos

    @property
    def MySectors(self) -> List[Tuple[Tuple[float, float], rect.Rect]]:
        mine = []
        sec_def = sec_u.rect_sector_attributes((self._area[2], self._area[3]), self.grid.Shape)
        for pos, _ in self.grid.grid_enumerator:
            _rect = (
                pos[1] * sec_def[0] + self._area[0],
                pos[0] * sec_def[1] + self._area[1],
                sec_def[0],
                sec_def[1]
            )

            mine.append((pos, _rect))

        return mine

    @property
    def Sectors(self) -> List[Tuple[Tuple[float, float], rect.Rect]]:
        childrens = []
        for pos, child in self.children.items():
            childrens += child.Sectors

        return self.MySectors + childrens

    @property
    def Area(self) -> rect.Rect:
        return self._area

    def plot(self,
             ax,
             nearby_pt: Tuple[float, float] = None,
             radius: float=None,
             pt_color: Color = None):
        # x_s = [point[0] for client, point in self.ClientsPos.items()]
        # y_s = [point[1] for client, point in self.ClientsPos.items()]

        # ax.scatter(x_s, y_s)
        plot_series([point for client, point in self.ClientsPos.items()], ax=ax, color=pt_color, series_type='scatter', zOrder=4)

        if nearby_pt is not None and radius is not None:
            nearbys = self.nearby_clients(pt=nearby_pt, radius=radius)
            # near_x_s = [point[0] for client, point in nearbys.items()]
            # near_y_s = [point[1] for client, point in nearbys.items()]
            plot_series([point for client, point in nearbys.items()], ax=ax, color=pt_color,
                        series_type='scatter', zOrder=4)
            # ax.scatter(near_x_s, near_y_s,)


        for _, sector in self.Sectors:
            rect = patches.Rectangle((sector[0], sector[1]), sector[2], sector[3], linewidth=1, edgecolor='r',
                                     facecolor='none')
            ax.add_patch(rect,)


if __name__ == "__main__":
    from cooptools.randoms import a_string
    import random as rnd
    import matplotlib.pyplot as plt
    import time
    from pprint import pprint


    rnd.seed(0)

    def test1():
        _rect = (0, 0, 400, 400)
        t0 = time.perf_counter()
        qt = SectorTree(area_rect=_rect,
                        shape=(3, 3),
                        capacity=1,
                        max_lvls=3)

        point_gen = lambda: (rnd.randint(0, _rect[2] - 1), rnd.randint(0, _rect[3] - 1))

        qt.add_update_client("a", point_gen())
        qt.add_update_client("b", point_gen())
        qt.add_update_client("a", point_gen())
        qt.add_update_client("c", point_gen())
        qt.add_update_client("d", point_gen())
        qt.add_update_client("e", point_gen())
        qt.add_update_client("f", point_gen())
        qt.add_update_client("g", point_gen())
        qt.add_update_client("h", point_gen())
        qt.add_update_client("i", point_gen())
        qt.add_update_client("j", point_gen())
        qt.add_update_client("k", point_gen())
        qt.add_update_client("l", point_gen())
        qt.add_update_client("a", point_gen())
        qt.add_update_client("b", point_gen())
        qt.add_update_client("c", point_gen())
        qt.add_update_client("d", point_gen())
        qt.add_update_client("e", point_gen())
        qt.add_update_client("f", point_gen())
        qt.add_update_client("g", point_gen())
        qt.add_update_client("h", point_gen())
        qt.add_update_client("i", point_gen())
        qt.add_update_client("j", point_gen())
        qt.add_update_client("k", point_gen())
        qt.add_update_client("l", point_gen())

        qt.add_update_client("a", point_gen())
        qt.add_update_client("b", point_gen())
        qt.add_update_client("a", point_gen())
        qt.add_update_client("c", point_gen())
        qt.add_update_client("d", point_gen())
        qt.add_update_client("e", point_gen())
        qt.add_update_client("a", (50, 50))

        t1 = time.perf_counter()
        print(f"Create time: {t1-t0}")

        pprint(qt.ClientMappings)
        fig, ax = plt.subplots()

        qt.plot(ax)
        plt.show(block=True)

    def test2():
        _rect = (0, 0, 400, 400)
        t0 = time.perf_counter()
        qt = SectorTree(area_rect=_rect,
                        shape=(3, 3),
                        capacity=1,
                        max_lvls=4)

        point_gen = lambda: (rnd.randint(0, _rect[2] - 1), rnd.randint(0, _rect[3] - 1))

        client_pos = []
        for ii in range(1000):
            client_pos.append((a_string(4), point_gen()))

        for client, pos in client_pos:
            qt.add_update_client(client, pos)

        t1 = time.perf_counter()
        print(f"Create time: {t1-t0}")

        fig, ax = plt.subplots()

        qt.plot(ax)
        plt.show(block=True)

    def test3():
        _rect = (0, 0, 400, 400)
        qt = SectorTree(area_rect=_rect,
                        shape=(3, 3),
                        capacity=1,
                        max_lvls=3)

        point_gen = lambda: (rnd.randint(0, _rect[2] - 1), rnd.randint(0, _rect[3] - 1))

        client_pos = []
        for ii in range(1000):
            client_pos.append((a_string(4), point_gen()))

        for client, pos in client_pos:
            qt.add_update_client(client, pos)

        radius = 100
        check = (50, 75)
        t0 = time.perf_counter()
        # nearbys = qt.nearby_clients(pt=check, radius=radius)

        t1 = time.perf_counter()
        print(f"Nearby time: {t1 - t0}")


        # PLOT
        fig, ax = plt.subplots()
        qt.plot(ax=ax,
                nearby_pt=check,
                radius=radius)

        plt.show()


    # test1()
    # test2()
    test3()