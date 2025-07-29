import numpy as np
from scipy.signal import convolve2d
from skimage.filters import threshold_otsu
from skimage.morphology import (
    remove_small_objects,
    binary_closing,
    skeletonize,
    disk
)
from skimage.measure import label
from skimage.draw import line
import matplotlib.pyplot as plt


def connect_close_endpoints(skel, max_gap=3):
    """
    Find all skeleton endpoints, and whenever two endpoints
    from different components lie within `max_gap` pixels
    of one another, draw a line between them.
    """
    # neighbor count kernel
    K = np.array([[1,1,1],
                  [1,0,1],
                  [1,1,1]])
    neigh = convolve2d(skel.astype(int), K, mode='same')
    endpoints = list(zip(*np.where((skel) & (neigh == 1))))
    used = set()
    for i, p in enumerate(endpoints):
        for j in range(i+1, len(endpoints)):
            q = endpoints[j]
            if np.hypot(p[0]-q[0], p[1]-q[1]) <= max_gap:
                # draw a line between p and q
                rr, cc = line(p[0], p[1], q[0], q[1])
                skel[rr, cc] = True
    return skel


def prune_skeleton(skel, max_spur_length=10):
    from scipy.signal import convolve2d
    K = np.array([[1,1,1],
                  [1,0,1],
                  [1,1,1]])
    H, W = skel.shape
    neigh = convolve2d(skel.astype(int), K, mode='same')
    endpoints = list(zip(*np.where((skel) & (neigh == 1))))
    to_remove = set()
    for ep in endpoints:
        path = [ep]
        prev = None
        cur = ep
        while True:
            r, c = cur
            nbrs = []
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==dc==0: continue
                    nr, nc = r+dr, c+dc
                    if (0 <= nr < H and 0 <= nc < W and skel[nr,nc] 
                        and (nr,nc) != prev):
                        nbrs.append((nr,nc))
            if len(nbrs) != 1:
                break
            prev, cur = cur, nbrs[0]
            path.append(cur)
            if neigh[cur] != 2:
                break
        if len(path) <= max_spur_length:
            to_remove.update(path)
    for r,c in to_remove:
        skel[r,c] = False
    return skel


def extract_main_path(skel):
    """
    As before: keep only the longest simple path in each component.
    """
    import numpy as np
    from collections import deque

    pts = list(zip(*np.where(skel)))
    idx = {p:i for i,p in enumerate(pts)}
    n = len(pts)

    nbrs = [[] for _ in range(n)]
    for i,(r,c) in enumerate(pts):
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==dc==0: continue
                q = (r+dr, c+dc)
                j = idx.get(q)
                if j is not None:
                    nbrs[i].append(j)

    seen = [False]*n
    main_idxs = set()
    for i in range(n):
        if seen[i]:
            continue
        comp = []
        dq = deque([i])
        seen[i] = True
        while dq:
            u = dq.popleft()
            comp.append(u)
            for v in nbrs[u]:
                if not seen[v]:
                    seen[v] = True
                    dq.append(v)

        ends = [u for u in comp if len(nbrs[u]) == 1]
        if len(ends) < 2:
            main_idxs.update(comp)
            continue

        def bfs(start):
            q = deque([start])
            parent = {start: None}
            while q:
                u = q.popleft()
                for v in nbrs[u]:
                    if v not in parent:
                        parent[v] = u
                        q.append(v)
            far = max(parent.keys(), key=lambda x: _bfs_dist(parent, x))
            return far, parent

        def _bfs_dist(parent, node):
            d = 0
            while parent[node] is not None:
                node = parent[node]
                d += 1
            return d

        u1, _ = bfs(ends[0])
        u2, parent = bfs(u1)
        cur = u2
        while cur is not None:
            main_idxs.add(cur)
            cur = parent[cur]

    new_skel = np.zeros_like(skel, dtype=bool)
    for u in main_idxs:
        r,c = pts[u]
        new_skel[r,c] = True

    return new_skel


def overlay_trace_centers(kymo,
                          min_size=50,
                          closing_radius=2,
                          max_spur_length=10,
                          connect_gap=3):
    """
    Extracts *unbranched* centerlines from a kymograph,
    connects near‐touching endpoints, and ensures
    one (x) pixel per y (time) for each trace.
    """
    # 1) Binarize
    th = threshold_otsu(kymo)
    bw = kymo > th

    # 2) Clean
    bw = remove_small_objects(bw, min_size=min_size)
    bw = binary_closing(bw, footprint=disk(closing_radius))

    # 3) Skeletonize, prune spurs, and stitch close endpoints
    skel = skeletonize(bw)
    skel = prune_skeleton(skel, max_spur_length)
    skel = connect_close_endpoints(skel, connect_gap)

    # 4) Keep only main paths
    skel = extract_main_path(skel)

    # 5) Enforce one pixel per y‐row
    H, W = skel.shape
    sk2 = np.zeros_like(skel, dtype=bool)
    for y in range(H):
        xs = np.flatnonzero(skel[y])
        if xs.size == 1:
            sk2[y, xs[0]] = True
        elif xs.size > 1:
            # pick the x with highest intensity in kymo
            best = xs[np.argmax(kymo[y, xs])]
            sk2[y, best] = True
    skel = sk2

    # 6) Label & color
    lbls = label(skel)
    base = ((kymo - kymo.min()) / max(np.ptp(kymo), 1) * 255).astype(np.uint8)
    rgb = np.dstack([base]*3)
    cmap = plt.get_cmap('hsv', lbls.max()+1)
    for lab in range(1, lbls.max()+1):
        mask = (lbls == lab)
        color = (np.array(cmap(lab)[:3]) * 255).astype(np.uint8)
        for c in range(3):
            rgb[..., c][mask] = color[c]

    return rgb