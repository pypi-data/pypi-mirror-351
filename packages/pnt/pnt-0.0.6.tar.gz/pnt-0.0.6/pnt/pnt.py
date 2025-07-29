"""
Package name: 'pnt' (Pubmed Network Toolkit)
Version number: 0.0.6 (released 2025-05-28)
Author: Jacob A. Rohde
Author_email: jarohde1@gmail.com
Description: A simple tool for generating and analyzing bibliometric citation network data from PubMed
Github url: https://github.com/jarohde/pnt
License: MIT
"""

__all__ = ['GetPubMedData', 'GetCitationNetwork', 'single_network_plot']

import pandas as pd
from datetime import datetime
import networkx as nx
import numpy as np
from math import nan

pd.options.mode.chained_assignment = None


class GetPubMedData:

    """
    A class object for extracting a citation data set from Pubmed.

    Arguments:

    - search_term: The only required parameter; takes a string object (or list of strings) as a keyword for
      searching PubMed papers.

    - pubmed_api_key: Optional string argument to set a PubMed NCBI API key as an environment variable. Doing so
      lessens rate limiting restrictions.

    - size: Optional integer argument to signify how many PubMed citations to pull; default set to 100 citations.
      GetPubMedData should only be used to extract limited or exploratory citation data sets.

    - start_date/end_date: Optional date arguments for GetPubMedData; default end date set to current date and
      default start date set to one week prior. Format should be string objects organized like 'YYYY, MM, DD'
      (e.g., start_date='2022, 5, 27' for May 27, 2022).

    Attributes:

    - GetPubMedData.citation_df: Extracts the PubMed citation data set as a pandas DataFrame object.

    Methods:

    - GetPubMedData.write_data(): Object method that writes the pandas DataFrame object to file. The method can take
      file_type and file_name as optional arguments. file_type indicates what file format to use when writing the data
      set and accepts a string argument of either 'json' or 'csv'; default set to 'json'. file_name takes a string to
      indicate what the file name should be saved as; default set to the search term provided.

    """

    def __init__(self, search_term, **kwargs):
        self.search_term = search_term
        self.pubmed_api_key = kwargs.get('pubmed_api_key', False)
        self.start_date = kwargs.get('start_date', None)
        self.end_date = kwargs.get('end_date', None)
        self.size = kwargs.get('size', 250)
        self.citation_df = pd.DataFrame

        if self.pubmed_api_key is not False and type(self.pubmed_api_key) == str:
            import os
            os.environ['NCBI_API_KEY'] = self.pubmed_api_key

        if self.end_date is None:
            today = str(datetime.now()).split(' ')[0].split('-')
            self.end_date = '/'.join(today)

        from metapub import PubMedFetcher
        fetch = PubMedFetcher()

        # Initialize metapub search
        try:
            pmids = fetch.pmids_for_query(query=self.search_term,
                                          since=self.start_date,
                                          until=self.end_date,
                                          retmax=self.size)

            self.pmids = pmids
            self.invalid_api = False

            pmid, first_author, last_author, author_list, title, journal, year, volume, issue, pages, url, abstract, \
                citation, doi = [], [], [], [], [], [], [], [], [], [], [], [], [], []

            for pmid_value in self.pmids:
                article_info = fetch.article_by_pmid(pmid_value)

                pmid.append(pmid_value)
                first_author.append(article_info.authors[0])
                last_author.append(article_info.authors[-1])
                author_list.append('; '.join(article_info.authors))
                title.append(article_info.title[0:-1])
                journal.append(article_info.journal)
                year.append(article_info.year)
                volume.append(article_info.volume)
                issue.append(article_info.issue)
                pages.append(article_info.pages)
                url.append(article_info.url)
                abstract.append(article_info.abstract)
                citation.append(article_info.citation)
                doi.append(article_info.doi)

            self.citation_df = pd.DataFrame(list(zip(pmid, first_author, last_author, author_list, title, journal, year,
                                                     volume, issue, pages, url, abstract, citation, doi)),
                                            columns=['pmid', 'first_author', 'last_author', 'author_list', 'title',
                                                     'journal', 'year', 'volume', 'issue', 'pages', 'url', 'abstract',
                                                     'citation', 'doi'])

        except Exception as e:
            if str(e) == 'Bad Request (400): API key invalid':
                print(f'EXCEPTION NOTED... {str(e).upper()}')
                self.invalid_api = True

    def __repr__(self):

        if self.invalid_api:
            message = "Invalid API key set; returned zero results."

        else:
            message = (f"PubMed citation data set:\n"
                       f"Search term(s): {self.search_term}\n"
                       f"Total dataframe size: {len(self.citation_df)}\n")

        return message

    def write_data(self, **kwargs):
        """
        A method for saving the PubMed citation data set to file.

        Arguments:

        - file_type: Accepts a string of either 'json' or 'csv'; default set to 'csv'.

        - file_name Accepts a string to indicate what the file name should be saved as; default set to the search term
          provided.

        """
        if self.invalid_api:
            print('Invalid API key set; cannot print results to file.')

        else:
            file_type = kwargs.get('file_type', 'csv')
            file_name = kwargs.get('file_name', self.search_term)

            if file_type.lower() != 'json' and file_type.lower() != 'csv' or type(file_type) != str:
                return 'Error: File type only supports .csv or .json extensions.'

            else:
                name = f'{file_name}.{file_type.lower()}'
                print(f'Writing {name} to file.')

                if file_type.lower() == 'json':
                    self.citation_df.to_json(name, orient='records', lines=True)

                if file_type.lower() == 'csv':
                    self.citation_df.to_csv(name, index=False, header=True, encoding='utf-8', na_rep='nan')


class GetCitationNetwork:
    """
    A class object for generating edge and node lists, and a NetworkX graph object from a PubMed citation data set.

    Arguments:

    - citation_dataset: The only required argument. Takes an existing citation data set or a GetPubMedData object.

    - edge_type: Optional string argument of either 'directed' or 'undirected' to signify network edge type; default
      set to directed.

    Attributes:

    - GetCitationNetwork.edge_list: Returns a pandas DataFrame of the network edge list with columns for the first
      author, each co-author, and the DOI of paper.

    - GetCitationNetwork.node_list: Returns a pandas DataFrame of the network node list with columns for unique nodes,
      and the node's in-degree and out-degree values.

    - GetCitationData.adjacency: Returns a dictionary of network adjacency matrices. By default, both weighted and
      unweighted matrices are returned. The dictionary will also return weighted adjacency matrices for each optional
      edge-based text attribute that users identified when creating the class.

    - GetCitationNetwork.graph: Returns a NetworkX graph object.

    Methods:

    - GetCitationData.write_data(): Object method that writes edge_list and node_list data sets to file. The method
      takes file_type, file_name, and adjacency as optional parameters. file_type indicates what file format to use when
      writing the data sets and accepts a string argument of either 'json' or 'csv'; default set to 'json'. file_name
      accepts a string to indicate what name to save the files as. adjacency accepts a boolean and indicates whether to
      write the data sets as adjacency matrices instead of edge and node lists.

    """

    def __init__(self, citation_df, **kwargs):

        self.citation_df = citation_df
        self.edge_type = kwargs.get('edge_type', 'directed')
        self.text_attribute = kwargs.get('text_attribute', False)
        self.edge_list = pd.DataFrame
        self.node_list = pd.DataFrame
        self.adjacency = dict
        self.graph = nx.Graph

        if 'GetPubMedData' in str(type(self.citation_df)):
            df = self.citation_df.citation_df

        else:
            df = self.citation_df

        # TODO: draft text attribute method for article titles/abstracts

        edge_first_author = []
        edge_co_author = []
        edge_journal = []

        for index, row in df.iterrows():
            author_list = row.author_list.split('; ')

            counter = 1
            for author in range(len(author_list) - 1):
                edge_first_author.append(author_list[0])
                edge_co_author.append(author_list[counter])
                edge_journal.append(row.journal)
                counter += 1

        edge_df = pd.DataFrame(list(zip(edge_first_author, edge_co_author, edge_journal)),
                               columns=['source', 'target', 'journal'])

        nodes = pd.Series(edge_first_author).unique()
        node_journals = []

        graph_object = nx.DiGraph()
        for node in nodes:
            graph_object.add_node(node)
            node_journal_list = []
            node_df = df.loc[df.author_list.apply(lambda x: x.split('; ')[0] == node)]

            for index, row in node_df.iterrows():
                node_journal_list.append(row.journal)
            node_journals.append(node_journal_list)

        for n1, n2 in zip(edge_df.source, edge_df.target):
            graph_object.add_edge(n1, n2)

        attrs = {}
        edge_list_index = 0
        for n1, n2 in zip(edge_df.source, edge_df.target):
            if (n1, n2) not in attrs.keys():
                edge_attr_dict = {}
                edge_attr_dict = {**edge_attr_dict, **{'weight': len(edge_df[(edge_df.source == n1) &
                                                                             (edge_df.target == n2)])}}

                # if self.text_attribute is not False:
                #     for col in text_attribute_columns:
                #         edge_attr_dict = {**edge_attr_dict, **{col: edge_df[col][edge_list_index]}}

                edge_list_index += 1
                attrs[(n1, n2)] = edge_attr_dict

            else:
                continue

        nx.set_edge_attributes(graph_object, attrs)

        degree = []
        for node in nodes:
            degree.append(graph_object.degree(node))

        node_df = pd.DataFrame(list(zip(nodes, degree, node_journals)),
                               columns=['node', 'degree', 'node_journals'])

        if self.edge_type.lower() == 'undirected':
            graph_object = graph_object.to_undirected()

        pandas_edge_list = nx.to_pandas_edgelist(graph_object)

        if len(pandas_edge_list) != 0:
            try:
                el_columns = ['source', 'target', 'weight']
                el_columns = el_columns + [column for column in edge_df.columns if column not in el_columns]
                pandas_edge_list = pandas_edge_list[el_columns]

            except Exception as e:
                el_columns = ['source', 'target', 'weight']
                pandas_edge_list = pandas_edge_list[el_columns]

        weighted_adj_matrix = nx.to_pandas_adjacency(graph_object)
        np.fill_diagonal(weighted_adj_matrix.values, nan)

        unweighted_adj_matrix = nx.to_pandas_adjacency(graph_object)
        unweighted_adj_matrix[unweighted_adj_matrix > 1] = 1
        np.fill_diagonal(unweighted_adj_matrix.values, nan)

        matrices = {'weighted_adj_matrix': weighted_adj_matrix,
                    'unweighted_adj_matrix': unweighted_adj_matrix}

        # text_attribute_columns = [column for column in pandas_edge_list.columns if 'text_attribute' in column]
        #
        # for column in text_attribute_columns:
        #     adj_matrix = nx.to_pandas_adjacency(graph_object)
        #     adj_matrix[:] = 0
        #
        #     for u, v, attribute in zip(pandas_edge_list.source, pandas_edge_list.target, pandas_edge_list[column]):
        #         if attribute == 'True':
        #             cell_loading = 1
        #
        #         else:
        #             cell_loading = 0
        #
        #         adj_matrix.at[u, v] = cell_loading
        #
        #     np.fill_diagonal(adj_matrix.values, nan)
        #     matrices[column + '_matrix'] = adj_matrix
        #
        self.node_list = node_df
        self.edge_list = pandas_edge_list
        self.adjacency = matrices
        self.graph = graph_object

    def __repr__(self):

        message = (f"Citation network object:\n"
                   f"Number of nodes: {len(self.node_list)}\n"
                   f"Number of edges: {len(self.edge_list)}")

        return message

    def write_data(self, **kwargs):
        """
        A method for saving the edge and node data to file.

        Parameter:

        - file_type: Accepts a string of either 'json' or 'csv'; default set to 'csv'.

        - file_name: Accepts a string to indicate what the edge and node list files should be saved as; default set to
          'edge_list' and 'node_list'.

        - adjacency: Accepts a boolean; default set to False. If True, adjacency matrices of the network (including
          matrices of any edge attributes) are saved as csv files.

        """

        file_type = kwargs.get('file_type', 'csv')
        file_name = kwargs.get('file_name', '')
        adjacency = kwargs.get('adjacency', False)

        if file_type.lower() != 'json' and file_type.lower() != 'csv' or type(file_type) != str:
            return 'Error: File type only supports .csv or .json extensions.'

        if adjacency:
            matrices = self.adjacency

            for matrix in matrices:
                if type(file_name) is str and file_name != '':
                    f_name = f'{matrix}_{file_name}.csv'
                else:
                    f_name = f'{matrix}.csv'

                print(f'Writing {f_name} to file.')
                matrices[matrix].to_csv(f_name, index=True, header=True, encoding='utf-8', na_rep='nan')

        else:
            file_list = ['node_list', 'edge_list']
            for file in file_list:
                if type(file_name) is str and file_name != '':
                    f_name = f'{file}_{file_name}'
                else:
                    f_name = file

                name = f'{f_name}.{file_type.lower()}'
                print(f'Writing {name} to file.')

                if file_type.lower() == 'json':
                    if file == 'node_list':
                        self.node_list.to_json(name, orient='records', lines=True)
                    else:
                        self.edge_list.to_json(name, orient='records', lines=True)

                if file_type.lower() == 'csv':
                    if file == 'node_list':
                        self.node_list.to_csv(name, index=False, header=True, encoding='utf-8', na_rep='nan')
                    else:
                        self.edge_list.to_csv(name, index=False, header=True, encoding='utf-8', na_rep='nan')


def single_network_plot(network, **kwargs):
    """
    A simple function for plotting networks via NetworkX and Matplotlib (additional install required). Please note this
    function is currently a work in progress and is meant to be basic tool to plot a single graph. See NetworkX
    documentation for more advanced plotting needs.

    Arguments:

    - network: The only required argument. Takes a GetCitationNetwork or NetworkX graph object.

    - title: Optional string argument to add a title to the plot.

    - pos: Optional string argument to set the NetworkX plotting algorithm. For ease of use, the argument currently
      accepts one of the following layout types as a string:

      - 'spring_layout' (default)
      - 'kamada_kawai_layout'
      - 'circular_layout'
      - 'random_layout'

    - **kwargs: The function also accepts several other NetworkX keyword arguments for plotting (please see NetworkX
      documentation for more info on these arguments). Currently accepted arguments include:

      - 'arrows' (bool)
      - 'arrowsize' (int)
      - 'edge_color' (str or list/array)
      - 'font_size' (int)
      - 'node_color' (str or list/array)
      - 'node_size' (str or list/array)
      - 'verticalalignment' (str)
      - 'width' (int/float or list/array)
      - 'with_labels' (bool)
    """

    import matplotlib.pyplot as plt

    if 'GetCitationNetwork' in str(type(network)):
        G = network.graph

    elif 'networkx.classes' in str(type(network)):
        G = network

    else:
        G = None

    # node attributes
    with_labels = kwargs.get('with_labels', False)
    node_color = kwargs.get('node_color', 'black')
    node_size = kwargs.get('node_size', 30)
    verticalalignment = kwargs.get('verticalalignment', 'center')
    font_size = kwargs.get('font_size', 8)

    # edge attributes
    edge_color = kwargs.get('edge_color', 'grey')
    width = kwargs.get('width', 1)
    arrows = kwargs.get('arrows', None)
    arrowsize = kwargs.get('arrowsize', 10)

    # general plot attributes
    title = kwargs.get('title', None)
    pos = kwargs.get('pos', 'spring_layout')

    plt.figure()
    plt.title(title)

    if G is not None:
        layouts = {'spring_layout': nx.spring_layout(G),
                   'kamada_kawai_layout': nx.kamada_kawai_layout(G),
                   'circular_layout': nx.circular_layout(G),
                   'random_layout': nx.random_layout(G)}

        pos = layouts.get(pos.lower(), 'spring_layout')

        plt_kwargs = {'pos': pos,
                      'edge_color': edge_color,
                      'node_color': node_color,
                      'with_labels': with_labels,
                      'verticalalignment': verticalalignment,
                      'font_size': font_size,
                      'node_size': node_size,
                      'width': width,
                      'arrows': arrows,
                      'arrowsize': arrowsize}

        nx.draw_networkx(G, **plt_kwargs)

        plt.show()

    else:
        print(f'Error: network argument expected GetCitationNetwork or networkx graph object; '
              f'received {type(network)} instead.')
