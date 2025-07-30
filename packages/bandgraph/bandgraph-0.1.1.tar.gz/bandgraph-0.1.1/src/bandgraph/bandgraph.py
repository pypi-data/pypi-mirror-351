import networkx as nx
import pandas as pd

def create_graph(dataframe: pd.DataFrame, coll=True) -> nx.Graph:

    # Create an empty graph
    graph = nx.Graph()
    
    # First, populate the graph nodes with all the considered bands 
    for i, band in dataframe.iterrows():

        graph.add_node(band["Band"], type="Band")

    # Second, add members
    for i, band in dataframe.iterrows():
        
        if band["Members"] is not None:

            for member in band["Members"].split(","):
                if not (member in graph):

                    graph.add_node(member, type="Musician")

                graph.add_edge(band["Band"], member, type="Member")
            
        # Then, add collaborations
        # If there are elements in the collaborations column
        if not dataframe['Collaborations'].isnull().values.sum()==len(dataframe):
            if coll and band["Collaborations"] is not None:
                for person in band["Collaborations"].split(","):
                    if not (person in graph):

                        graph.add_node(person, type="Musician")

                    if not graph.has_edge(band["Band"], person):
                        graph.add_edge(band["Band"], person, type="Collaboration")
            
        
    return graph

def load_data(filename: str) -> pd.DataFrame:

    dataframe = pd.read_csv(filename, sep=';', names=['Band', 'Members', 'Collaborations'])
    dataframe = dataframe.where(pd.notna(dataframe), None)

    return dataframe