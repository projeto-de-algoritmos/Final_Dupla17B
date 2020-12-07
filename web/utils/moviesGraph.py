class MoviesGraph(object): 
    '''
    Our Movies graph class
    '''

    def __init__(self, movies): 
        '''
        Builds an adjacency list with all the movies and genres
        Also builds a list just with the movie names for later use 
        '''
        self.movies_graph = {}
        self.movies_list = []

        for movie in movies:

            movie_name = movie.get("movie")
            movie_genres = movie.get("genres")
            movie_thumb = movie.get("thumbnail")
            movie_link = movie.get("link")

            if movie_name not in self.movies_graph:
                self.movies_list.append((movie_name, movie_thumb, movie_link))

                # adds movie to graph
                self.movies_graph[movie_name] = []
                for genre in movie_genres:

                    # adds genre to movie
                    self.movies_graph[movie_name].append(genre)

                    # adds movie to genre
                    if genre not in self.movies_graph:
                        # also adds genre to graph
                        self.movies_graph[genre] = [movie_name]
                    else:
                        self.movies_graph[genre].append(movie_name)

    def get_movies_list(self):
        
        return self.movies_list

    def get_movies_graph(self):
        
        return self.movies_graph

    def predecessor(self, start):
        '''
        Receives a starting node 
        and returns a dict with the predecessors
        of each node in the graph
        '''
        G = self.movies_graph
        if start not in G:
            raise False

        level = 0  
        nextlevel = [start]  
        explored = {start: level}  
        pred = {start: []}  
        while nextlevel:
            level = level + 1
            thislevel = nextlevel
            nextlevel = []
            for v in thislevel:
                for w in G[v]:
                    if w not in explored:
                        pred[w] = [v]
                        explored[w] = level
                        nextlevel.append(w)
                    elif explored[w] == level:  
                        pred[w].append(v)  

        return pred

    def find_paths(self, start, target, pred):
        '''
        Receives an initial node, a target node and a dict of all the nodes predecessors
        Generates an object with all the shortest paths between start and target node
        '''
        if target not in pred or {target}==start:
            return None

        explored = {target}
        stack = [[target, 0]]
        top = 0
        while top >= 0:
            node, i = stack[top]
            if node in start:
                yield [p for p, n in reversed(stack[: top + 1])]
            if len(pred[node]) > i:
                stack[top][1] = i + 1
                next = pred[node][i]
                if next in explored:
                    continue
                else:
                    explored.add(next)
                top += 1
                if top == len(stack):
                    stack.append([next, 0])
                else:
                    stack[top][:] = [next, 0]
            else:
                explored.discard(node)
                top -= 1

    def get_movie_recommendations(self, user_movie):
        '''
        Receives a movie name and returns a list 
        of movies sorted by the length and the number of shortest paths
        to the starting movie
        '''

        recommendations = []

        # for each movie in the list, keep the length and the number of shortest paths 
        for movie, thumb, link in self.movies_list:

            # get parentage
            parentage = self.predecessor(movie)

            # get paths
            paths = list(self.find_paths({movie}, user_movie, parentage))
            if paths != []:
                num_paths = len(paths)
                path_lenght = len(paths[0])
                
                # disconsidering any path length higher than five. As they would represent too weak relationships
                if path_lenght <=5:
                    recommendations.append({'name':movie,'lenght':path_lenght,
                            'number':num_paths, 'thumbnail':thumb, 'link':link})

        # sorting the list by the lenght of the shortest path and the number of shortest paths
        return sorted(recommendations, key=lambda k: (k['lenght'], -k['number']))
