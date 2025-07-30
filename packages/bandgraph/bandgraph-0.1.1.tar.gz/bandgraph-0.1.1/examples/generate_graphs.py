import glob
from ipysigma import Sigma

from bandgraph import create_graph, load_data

datapath = "../data/"

# Whether to show collaborations
show_colls = True

# Arguments for the Sigma graph
args = {"node_size":0,
        "node_color":"type",
        "edge_color":"type",
        "label_density":10,
        "node_border_color_from":"node",
        "start_layout":2,
        "hide_info_panel":True,
        "background_color":"rgb(255, 255, 255)"}

datafiles = sorted(glob.glob(datapath+"*txt"))

for filename in datafiles:
    dataname = filename.replace(".txt","").replace(datapath,"")
    print(dataname)
    
    dataframe = load_data(filename)

    graph = create_graph(dataframe, coll=show_colls)
    args["node_size"] = graph.degree
    
    sig = Sigma(graph, **args)
    
    sig.write_html(graph,"../graphs/"+dataname+'.html', fullscreen=True, **args)