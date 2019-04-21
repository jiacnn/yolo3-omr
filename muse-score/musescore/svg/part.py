from dataclasses import dataclass, field
from lxml.etree import _Element as Element
from lxml.etree import _ElementTree as ElementTree


@dataclass
class Point:
    x: float
    y: float


@dataclass
class BoundingBox:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def center(self) -> Point:
        return Point((self.xmin + self.xmax) / 2, (self.ymin + self.ymax) / 2)


@dataclass
class Symbol:
    is_path: bool = field(default=False)
    type: str = field(default='UNINITIALIZED')
    bbox: BoundingBox = field(default=None)
    svg: Element = field(default=None)


@dataclass
class Page:
    width: float = field(default=0)
    height: float = field(default=0)
    symbols: [Symbol] = field(default_factory=list)

    def by_class(self, name) -> [Symbol]:
        return list(filter(lambda s: s.type == name, self.symbols))

    def all_path(self) -> [Symbol]:
        return list(filter(lambda s: s.is_path, self.symbols))

    def all_polyline(self) -> [Symbol]:
        return list(filter(lambda s: not s.is_path, self.symbols))

    @staticmethod
    def cluster_by_y(symbols: [Symbol], ys: [float]) -> {float: [Symbol]}:
        cluster = {x: [] for x in ys}
        for symbol in symbols:
            center = min(cluster, key=lambda c: abs(symbol.bbox.center.y - c))
            cluster[center].append(symbol)
        for paths in cluster.values():
            paths.sort(key=lambda p: p.bbox.xmin)
        return cluster

    def rearrange(self):
        # TODO: use KD-Tree to accumulate all this staff :P
        lines = sorted(self.by_class('StaffLines'), key=lambda s: s.bbox.ymin)
        staffline_margin = lines[1].bbox.ymin - lines[0].bbox.ymin
        staffline_center_ys = [line.bbox.ymin for line in lines[2::5]]
        staffline_xmin, staffline_xmax = lines[0].bbox.xmin, lines[0].bbox.xmax
        cluster = self.cluster_by_y(self.all_path(), staffline_center_ys)
        # cut by measure
        bars = self.by_class('BarLine')
        # add dummy bar-lines at every beginning
        for y in staffline_center_ys:
            y -= 2 * staffline_margin
            bars.append(Symbol(bbox=BoundingBox(xmin=staffline_xmin, xmax=staffline_xmax, ymin=y, ymax=y)))
        bars = sorted(bars, key=lambda s: (s.bbox.ymin, s.bbox.xmin))
        measures = []
        for left, right in zip(bars, bars[1:]):
            # ignore this pair if not in same line, or too close
            if left.bbox.ymin != right.bbox.ymin or right.bbox.xmin - left.bbox.xmin < staffline_margin:
                continue
            measures.append(Symbol(type='Measure',
                                   bbox=BoundingBox(xmin=left.bbox.xmin, xmax=right.bbox.xmax,
                                                    ymin=left.bbox.ymin, ymax=right.bbox.ymax)))
        measure_cluster = self.cluster_by_y(measures, staffline_center_ys)
        rearranged_measures = []
        for center, measures in measure_cluster.items():
            for measure in measures:
                xmin, xmax = measure.bbox.xmin, measure.bbox.xmax
                symbols = [s for s in cluster[center] if xmin < s.bbox.xmin < s.bbox.xmax < xmax]
                rearranged_measures.append((measure, symbols))
        return rearranged_measures

    @staticmethod
    def couple_note_dot(symbols):
        pass
