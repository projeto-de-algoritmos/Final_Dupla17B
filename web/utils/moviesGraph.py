class MoviesGraph(object): 
  
    # default constructor 
    def __init__(self, movies): 
        self.movies_graph = {}
        self.movies_list = []

        for movie in movies:

            movie_name = movie.get("movie")
            movie_genres = movie.get("genres")
            movie_thumb = movie.get("thumbnail")
            movie_link = movie.get("link")

            if movie_name not in self.movies_graph:
                self.movies_list.append((movie_name, movie_thumb, movie_link))
                self.movies_graph[movie_name] = []
                for genre in movie_genres:
                    self.movies_graph[movie_name].append(genre)
                    if genre not in self.movies_graph:
                        #adiciona genero ao grafo
                        self.movies_graph[genre] = [movie_name]
                    else:
                        #adiciona filme a genero
                        self.movies_graph[genre].append(movie_name)

    def get_movies_list(self):
        
        return self.movies_list

    def get_movies_graph(self):
        
        return self.movies_graph

    def predecessor(self, start):
        '''
        Recebe o grafo e o nó inicial
        Retorna uma  dict de "pais" pra cada nó
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
        Recebe um nó inicial, um nó final e um dicionario contendo os pais de cada nó
        Gera um objeto com todos os menores caminhos entre o nó inicial e o nó final
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
        recommendations = []

        #para cada filme na lista de musicas, guardar o tamanho do menor caminho e o número de menores caminhos
        for movie, thumb, link in self.movies_list:
            parentage = self.predecessor(movie)
            paths = list(self.find_paths({movie}, user_movie, parentage))
            if paths != []:
                num_paths = len(paths)
                path_lenght = len(paths[0])
                
                #não consideramos caminhos com comprimento maior que 5 pois isso seria uma relação muito fraca.
                if path_lenght <=5:
                    recommendations.append({'name':movie,'lenght':path_lenght,
                            'number':num_paths, 'thumbnail':thumb, 'link':link})

        #ordenamos as sugestões por comprimento do caminho mais curto e quantidade de caminhos mais curtos
        return sorted(recommendations, key=lambda k: (k['lenght'], -k['number']))
