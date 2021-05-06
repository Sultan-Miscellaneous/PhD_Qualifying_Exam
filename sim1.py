# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from itertools import product as vanilla_product
from tqdm.contrib.itertools import product
from collections import Counter


# %%
weights_M  = 3
weights_N  = 3
ifmap_M = 224
ifmap_N = 224
channels = 1
ofmap_M = ifmap_M-weights_M+1
ofmap_N = ifmap_N-weights_M+1
ofmap_C = 1


# %%
ifmap = np.arange(channels*ifmap_M*ifmap_N).reshape(channels,ifmap_M,ifmap_N)


# %%
weights = np.arange(channels*weights_M*weights_N).reshape(channels,weights_M,weights_N)


# %%
pads = sliding_window_view(ifmap,window_shape=[1,3,3]).squeeze()


# %%
pad_origin = {}
for p_i, p_j in product(range(pads.shape[0]), range(pads.shape[1])):
    for w_i, w_j in vanilla_product(range(pads.shape[2]), range(pads.shape[3])):
        cur_ifmap = pads[p_i, p_j, w_i, w_j]
        origin = {"pad_idx": (p_i, p_j), "weight_idx": (w_i, w_j)}
        if cur_ifmap not in pad_origin.keys():
            pad_origin[cur_ifmap] = [origin]
        else:
            pad_origin[cur_ifmap].append(origin)


# %%
relevant_pads = set()
for idx in range(0,450):
    for entry in pad_origin[idx]:
        relevant_pads.update([entry['pad_idx']])


# %%
len(relevant_pads)


# %%
macs = 0
for idx in range(0,ifmap_M*ifmap_N*channels):
    macs += len(pad_origin[idx])
print(macs/(ifmap_M*ifmap_N*channels))


# %%
output = []
pad_completion_counter = Counter()
for k, i, j in product(range(channels), range(ifmap_M), range(ifmap_N)):
    output_added = False
    for assosciated_pads in pad_origin[ifmap[k][i][j]]:
        pad_idx = assosciated_pads['pad_idx']
        pad_completion_counter[pad_idx] += 1
        if pad_completion_counter[pad_idx] == 9:
            output.append(np.einsum('ij,ij', pads[pad_idx], weights.squeeze()))
            output_added = True
    if not output_added:
        output.append(0)
            
output.extend([0]*224)

# %%
output = np.array(output).reshape(1,224,224)

# %%
output

# %%
