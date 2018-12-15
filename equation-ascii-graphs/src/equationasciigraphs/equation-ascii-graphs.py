'''
Created on 1 Dec 2018

@author: JRVeale
'''

#imports
import math
from asteval import Interpreter
aeval = Interpreter()

#defintions
def get_user_dim():
    default = 30
    min = 4
    max = 500
    user_str = input("Enter render size ")
    if user_str in [""," "]:
        return default
    else:
        user_int = int(user_str)
        if user_int < min or user_int > max:
            return default
        else:
            return user_int

def get_user_folder():
    user_str = input("Enter folder for graph ")
    raw_str = "%r"%user_str[1:len(user_str)-1]
    print(user_str)
    return user_str

def get_user_equation():
    user_str = input("Enter an equation ")
    if user_str in [""," "]:
        return "x"  #default graph is y=x
    #convert into Python equivalent where necessary
    output = user_str #replace with above
    return output

def get_user_range():
    default = [-100,100,-100,100]
    try:
        user_in = input("Enter a range in format xMin, xMax, yMin, yMax ")
        if(user_in in [""," "]):
            print("No input for range")
            return default
        aeval("user_range = [" + user_in + "]")
        user_range = aeval.symtable['user_range']
    except:
        print("Bad input for range")
        return default
    #ensure at least 4 items in list
    if (len(user_range) < 4):
        print("Not enough inputs for range")
        return default
    #ensure min is less than max
    for i in [0,2]:
        if (user_range[i] == user_range[i+1]):
            if(user_range[i] == 0):
                user_range[i+1] = 1
            else:
                user_range[i+1] *= 1.01
        if (user_range[i] > user_range[i+1]):
            user_range[i], user_range[i+1] = user_range[i+1], user_range[i]
    #ensure only 4 values, rest ignored
    return user_range[0:4]

def makeEven(num):
    if(num %2 != 0):
        num+=1
    return num

def gen_blank_array(width,height):
    return [[" " for i in range(width)] for j in range(height)]

def zero_in_bounds(bounds):
    if ((bounds[0] <= 0) and (bounds[1] >= 0)):
        return True
    else:
        return False

def get_interval(bounds,dimension):
    interval = (bounds[1]-bounds[0])/(2*dimension)
    return interval

def get_intervals(bounds, x_dim, y_dim):
    x_interval = get_interval([bounds[0],bounds[1]],x_dim)
    y_interval = get_interval([bounds[2],bounds[3]],y_dim)
    return [x_interval,y_interval]

def plot(equation,bounds,dimension):
    y_dim = makeEven(dimension)
    x_dim = makeEven(math.ceil(y_dim*2))
    graph = gen_blank_array(x_dim,y_dim)

    #add axes lines (for each axis: check if 0 in range - put line on zero, else just edge
    temp = get_intervals(bounds,x_dim,y_dim)
    x_int = temp[0]
    y_int = temp[1]
    #should be able to tidy below using min & max's...
    if(not zero_in_bounds([bounds[2],bounds[3]])):
        #put axis at edge
        for i in range(x_dim):
            graph[y_dim-1][i] = "_"
    else:
        #put axis in correct spot
        for i in range(x_dim):
            if (bounds[2] == 0):
                line_pos = (y_dim-1)
            else:
                line_pos = int((-bounds[2]/(2*y_int))-1)
            graph[line_pos][i] = "_"

    #move y axis to be drawn AFTER line (looks better I think)
    if(not zero_in_bounds([bounds[0],bounds[1]])):
        #put axis at edge
        for j in range(y_dim):
            graph[j][0] = "|"
    else:
        #put axis in correct spot
        for j in range(y_dim):
            if (bounds[0] == 0):
                line_pos = 0
            else:
                line_pos = int((-bounds[0]/(2*x_int))-1)
            graph[j][line_pos] = "|"
            
    #print to check progress
    for j in range(y_dim):
        for i in range(x_dim):
            print(graph[j][i],end="")
            if (i == x_dim-1):
                print()
    
    #use intervals to get x values to compute, then get values for y
    x_values = [float(bounds[0])]*(x_dim*2+1)
    for a in range(1,len(x_values)):
        x_values[a] = x_values[a-1] + x_int
    print(x_values)
    y_values = [0.0]*(x_dim*2+1)
    aeval('x = 0')
    for b in range(len(y_values)):
        aeval.symtable['x'] = x_values[b]
        #x = x_values[b]
        temp_eq = 'temp = ' + equation
        #print(temp_eq)
        aeval(temp_eq)
        y_values[b] = float(aeval.symtable['temp'])
        #print(y_values[b])
    print(y_values)
    print()
    
    #get points (x,y) in array positions
    x_posits = [0.0]*(x_dim*2+1)
    for c in range(1,len(x_posits)):
        x_posits[c] = x_posits[c-1] + 0.5
    print(x_posits)
    y_posits = y_values
    #normalise, such that y values between 0 & 2(y_dim-1)
    y_posits[:] = [(((n-bounds[2])/(bounds[3]-bounds[2]))*(2*(y_dim-1))) for n in y_posits]
    #round to nearest int and then halve (cancels 2 from previous to result in rounded to nearest .5)
    y_posits[:] = [round(n)/2 for n in y_posits]
    print(y_posits)
    
    #determine chars and where they go, then add to array (over spaces)
    for n in range(len(x_posits)-2):
        if n%2 == 0: #only do these checks at the beginning of each 'square' in graph
            print("n:",end="")
            print(n,end=" ")
            if (y_posits[n] < 0 and y_posits[n+1] < 0 and y_posits[n+2] < 0) or (y_posits[n] > y_dim and y_posits[n+1] > y_dim and y_posits[n+2 > y_dim]):
                print("y out of range")
                None
                #no point to plot
            else:
                print("y in range",end=" ")
                y_place = y_dim - (int(math.floor(y_posits[n]))+1)
                if(y_place <= 0): #prevents wraparound...
                    print("wraparound prevented!")
                    None
                else:
                    if(y_posits[n] == y_posits[n+1] and y_posits[n+1] == y_posits[n+2]): #_ or -
                        if((2*y_posits[n])%2 == 0): #_
                            print("printed a '_' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place,end=" - ")
                            print("1")
                            graph[y_place][int(x_posits[n])] = '_'
                        else: #-
                            print("printed a '-' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place,end=" - ")
                            print("2")
                            graph[y_place][int(x_posits[n])] = '-'
                    elif(y_posits[n] == y_posits[n+2] and (y_posits[n+1] == y_posits[n]+0.5 or y_posits[n+1] == y_posits[n]+1)): #^
                        print("printed a '^' in x_place:",end="")
                        print(n,end=" y_place_")
                        print(y_place-1,end=" - ")
                        print("3")
                        graph[y_place-1][int(x_posits[n])] = '^'
                    elif(y_posits[n] == y_posits[n+2] and (y_posits[n+1] == y_posits[n]-0.5 or y_posits[n+1] == y_posits[n]-1)): #^
                        print("printed a '^' in x_place:",end="")
                        print(n,end=" y_place_")
                        print(y_place,end=" - ")
                        print("4")
                        graph[y_place][int(x_posits[n])] = 'v'
                    elif(y_posits[n] == y_posits[n+2] - 0.5): #/
                        if((2*y_posits[n])%2 == 0): #/
                            print("printed a '/' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place,end=" - ")
                            print("5")
                            graph[y_place][int(x_posits[n])] = '/'
                        else:
                            print("printed a '_' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place-1,end=" - ")
                            print("6")
                            graph[y_place-1][int(x_posits[n])] = '_'
                    elif(y_posits[n] == y_posits[n+2] + 0.5): #\
                        if((2*y_posits[n])%2 == 0): #\
                            print("printed a '\\' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place,end=" - ")
                            print("7")
                            graph[y_place][int(x_posits[n])] = '\\'
                        else:
                            print("printed a '_' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place-1,end=" - ")
                            print("8")
                            graph[y_place-1][int(x_posits[n])] = '_'
                    elif(y_posits[n] <= y_posits[n+2] - 0.5 or y_posits[n] >= y_posits[n+2] + 0.5): #|
                        if((2*y_posits[n])%2 == 0): #|
                            print("printed a '|' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place,end=" - ")
                            print("9")
                            graph[y_place][int(x_posits[n])] = '|'
                        else:
                            print("printed a '|' in x_place:",end="")
                            print(n,end=" y_place_")
                            print(y_place-1,end=" - ")
                            print("10")
                            graph[y_place-1][int(x_posits[n])] = '|'
                        #TODO: extend '|' vertically when needed
    #print to check progress
    for j in range(y_dim):
        for i in range(x_dim):
            print(graph[j][i],end="")
            if (i == x_dim-1):
                print()    
    
    #TODO: add axes labels
    return graph

#TODO: make this OOP (all in a class, with object variables instead of passing around varibles from function to function like an idiot)

def graph_to_txt(graph,location,filename):
    import os
    path = os.path.join(location,filename)
    if not os.path.exists(location):
        os.makedirs(location)
    f = open(path + ".txt","w+")
    for j in range(len(graph)):
        for i in range(len(graph[0])):
            f.write(graph[j][i])
            if (i == len(graph[0])-1):
                f.write("\r\n")
    f.close()
    return None

def main():
    #get user input (and clean)
    eq = get_user_equation() #can call eval(eq) for all x's needed
    print("Python equation is " + eq)
    axes_range = get_user_range()
    dim = get_user_dim()
    print("Graph range is X from "+str(axes_range[0])+" to "+str(axes_range[1])+" and Y from "+str(axes_range[2])+" to "+str(axes_range[3]))
    #make 2d char array and fill with " " (spaces)
    ascii_graph = plot(eq,axes_range,dim)
    #replace spaces with symbols as per get_y(x) ("_-^v/\|",axes,axis lables)
    
    #turn 2d char array into text file
    folder = get_user_folder()
    graph_to_txt(ascii_graph,folder,"test")
    return None

#Allow code to run if this module is run directly, but don't run if imported...
if __name__ == "__main__":
    while True:
        main()