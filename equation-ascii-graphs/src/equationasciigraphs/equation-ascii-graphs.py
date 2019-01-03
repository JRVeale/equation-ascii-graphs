'''
Created on 1 Dec 2018

@author: JRVeale
'''

#imports
import math
from asteval import Interpreter

class AsciiGraph:
    """A class for generating ASCII symbol graphs"""
    def __init__(self,equation,axes_range,plot_size,x_y_ratio):
        #need options for leaving inputs blank...
        self.aeval = Interpreter()
        self.eq = self.parse_eq(equation)
        self.ranges = self.parse_ranges(axes_range)
        self.dim = self.parse_dim(plot_size)
        self.ratio = x_y_ratio
        self.array = self.plot()
    
    def parse_eq(self,equation):
        #user_str = input("Enter an equation ")
        if equation in [""," "]:
            return "x"  #default graph is y=x
        #TODO: convert into Python equivalent where necessary
        output = equation #replace with above
        return output
    
    def parse_ranges(self,axes_range):
        default = [-100,100,-100,100]
        try:
            #user_in = input("Enter a range in format xMin, xMax, yMin, yMax ")
            if(axes_range in [""," "]):
                print("No input for range")
                return default
            self.aeval("user_range = " + str(axes_range))
            user_range = self.aeval.symtable['user_range']
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
    
    def parse_dim(self,plot_size):
        default = 30
        min = 4
        max = 500
        if plot_size in [""," "]:
            return default
        else:
            plot_size_int = int(plot_size)
            if plot_size_int < min or plot_size_int > max:
                return default
            else:
                return plot_size_int
    
    def makeEven(self,num):
        if(num %2 != 0):
            num+=1
        return num
    
    def gen_blank_array(self,width,height):
        return [[" " for i in range(width)] for j in range(height)]
    
    def zero_in_bounds(self,bounds):
        if ((bounds[0] <= 0) and (bounds[1] >= 0)):
            return True
        else:
            return False
    
    def get_interval(self,bounds,dimension):
        interval = (bounds[1]-bounds[0])/(2*dimension)
        return interval
    
    def get_intervals(self, bounds, x_dim, y_dim):
        x_interval = self.get_interval([bounds[0],bounds[1]],x_dim)
        y_interval = self.get_interval([bounds[2],bounds[3]],y_dim)
        return [x_interval,y_interval]
    
    def plot(self):
        #plot function here
        
        y_dim = self.makeEven(self.dim)
        x_dim = self.makeEven(math.ceil(y_dim*self.ratio))
        graph = self.gen_blank_array(x_dim,y_dim)
    
        #add axes lines (for each axis: check if 0 in range - put line on zero, else just edge
        #TODO: Change below to x_int, y_int = get_intervals(self.ranges,x_dim,y_dim)
        temp = self.get_intervals(self.ranges,x_dim,y_dim)
        x_int = temp[0]
        y_int = temp[1]
        #should be able to tidy below using min & max's...
        if(not self.zero_in_bounds([self.ranges[2],self.ranges[3]])):
            #put axis at edge
            for i in range(x_dim):
                graph[y_dim-1][i] = "_"
        else:
            #put axis in correct spot
            for i in range(x_dim):
                if (self.ranges[2] == 0):
                    line_pos = (y_dim-1)
                else:
                    line_pos = int((-self.ranges[2]/(2*y_int))-1)
                graph[line_pos][i] = "_"
    
        #move y axis to be drawn AFTER line (looks better I think)
        if(not self.zero_in_bounds([self.ranges[0],self.ranges[1]])):
            #put axis at edge
            for j in range(y_dim):
                graph[j][0] = "|"
        else:
            #put axis in correct spot
            for j in range(y_dim):
                if (self.ranges[0] == 0):
                    line_pos = 0
                else:
                    line_pos = int((-self.ranges[0]/(2*x_int))-1)
                graph[j][line_pos] = "|"
        '''        
        #print to check progress
        for j in range(y_dim):
            for i in range(x_dim):
                print(graph[j][i],end="")
                if (i == x_dim-1):
                    print()
        '''
        #use intervals to get x values to compute, then get values for y
        x_values = [float(self.ranges[0])]*(x_dim*2+1)
        for a in range(1,len(x_values)):
            x_values[a] = x_values[a-1] + x_int
        #print(x_values)
        y_values = [0.0]*(x_dim*2+1)
        self.aeval('x = 0')
        for b in range(len(y_values)):
            self.aeval.symtable['x'] = x_values[b]
            #x = x_values[b]
            temp_eq = 'temp = ' + self.eq
            #print(temp_eq)
            self.aeval(temp_eq)
            y_values[b] = float(self.aeval.symtable['temp'])
            #print(y_values[b])
        #print(y_values)
        #print()
        
        #get points (x,y) in array positions
        x_posits = [0.0]*(x_dim*2+1)
        for c in range(1,len(x_posits)):
            x_posits[c] = x_posits[c-1] + 0.5
        #print(x_posits)
        y_posits = y_values
        #normalise, such that y values between 0 & 2(y_dim-1)
        y_posits[:] = [(((n-self.ranges[2])/(self.ranges[3]-self.ranges[2]))*(2*(y_dim-1))) for n in y_posits]
        #round to nearest int and then halve (cancels 2 from previous to result in rounded to nearest .5)
        y_posits[:] = [round(n)/2 for n in y_posits]
        #print(y_posits)
        
        #determine chars and where they go, then add to array (over spaces)
        for n in range(len(x_posits)-2):
            if n%2 == 0: #only do these checks at the beginning of each 'square' in graph
                #print("n:",end="")
                #print(n,end=" ")
                if (y_posits[n] < 0 and y_posits[n+1] < 0 and y_posits[n+2] < 0) or (y_posits[n] > y_dim and y_posits[n+1] > y_dim and y_posits[n+2 > y_dim]):
                    #print("y out of range")
                    None
                    #no point to plot
                else:
                    #print("y in range",end=" ")
                    y_place = y_dim - (int(math.floor(y_posits[n]))+1)
                    if(y_place <= 0): #prevents wraparound...
                        #print("wraparound prevented!")
                        None
                    elif(y_place > y_dim):
                        #print("overprint prevented!")
                        None
                    else:
                        if(y_posits[n] == y_posits[n+1] and y_posits[n+1] == y_posits[n+2]): #_ or -
                            if((2*y_posits[n])%2 == 0): #_
                                #print("printed a '_' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place,end=" - ")
                                #print("1")
                                graph[y_place][int(x_posits[n])] = '_'
                            else: #-
                                #print("printed a '-' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place,end=" - ")
                                #print("2")
                                graph[y_place][int(x_posits[n])] = '-'
                        elif(y_posits[n] == y_posits[n+2] and (y_posits[n+1] == y_posits[n]+0.5 or y_posits[n+1] == y_posits[n]+1)): #^
                            #print("printed a '^' in x_place:",end="")
                            #print(n,end=" y_place_")
                            #print(y_place-1,end=" - ")
                            #print("3")
                            graph[y_place-1][int(x_posits[n])] = '^'
                        elif(y_posits[n] == y_posits[n+2] and (y_posits[n+1] == y_posits[n]-0.5 or y_posits[n+1] == y_posits[n]-1)): #^
                            #print("printed a '^' in x_place:",end="")
                            #print(n,end=" y_place_")
                            #print(y_place,end=" - ")
                            #print("4")
                            graph[y_place][int(x_posits[n])] = 'v'
                        elif(y_posits[n] == y_posits[n+2] - 0.5): #/
                            if((2*y_posits[n])%2 == 0): #/
                                #print("printed a '/' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place,end=" - ")
                                #print("5")
                                graph[y_place][int(x_posits[n])] = '/'
                            else:
                                #print("printed a '_' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place-1,end=" - ")
                                #print("6")
                                graph[y_place-1][int(x_posits[n])] = '_'
                        elif(y_posits[n] == y_posits[n+2] + 0.5): #\
                            if((2*y_posits[n])%2 == 0): #\
                                #print("printed a '\\' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place,end=" - ")
                                #print("7")
                                graph[y_place][int(x_posits[n])] = '\\'
                            else:
                                #print("printed a '_' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place-1,end=" - ")
                                #print("8")
                                graph[y_place-1][int(x_posits[n])] = '_'
                        elif(y_posits[n] <= y_posits[n+2] - 0.5 or y_posits[n] >= y_posits[n+2] + 0.5): #|
                            if((2*y_posits[n])%2 == 0): #|
                                #print("printed a '|' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place,end=" - ")
                                #print("9")
                                graph[y_place][int(x_posits[n])] = '|'
                            else:
                                #print("printed a '|' in x_place:",end="")
                                #print(n,end=" y_place_")
                                #print(y_place-1,end=" - ")
                                #print("10")
                                graph[y_place-1][int(x_posits[n])] = '|'
                            #TODO: extend '|' vertically when needed
        '''
        #print to check progress
        for j in range(y_dim):
            for i in range(x_dim):
                print(graph[j][i],end="")
                if (i == x_dim-1):
                    print()    
        '''
        #TODO: add axes labels
        return graph
    
    def save(self,folder,filename):
        """Saves the .txt file of the graph, in "folder\filename.txt" """
        import os
        path = os.path.join(folder,filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        f = open(path + ".txt","w+")
        for j in range(len(self.array)):
            for i in range(len(self.array[0])):
                f.write(self.array[j][i])
                if (i == len(self.array[0])-1):
                    f.write("\r\n")
        f.close()

#############################################################
# Demo script
#############################################################
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
    aeval = Interpreter()
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

def demo():
    print("Starting Demo")
    print("This demo is shown only when running this module directly.")
    print("Follow the instructions to understand how to use the library.")
    print()
    print("Create an instance of the AsciiGraph class to generate an array of ASCII chars representing a simple equation")
    print("a = AsciiGraph(equation,axes_range,plot_size,x_y_ratio)")
    print("\tequation is a string representing the RHS of a y = f(x) equation, written in a format parseable by Python")
    print("\taxes_range is a list of four numbers representing the min and max x values, and min and max y values to plot, in that order")
    print("\tplot_size is the number of rows of characters to render in the graph - the number of columns will be set to make the graph square visually")
    print("\tx_y_ratio is the visual ratio of characters. For a .txt file open in notepad this should be 2. This can be set to adjust the 'squareness' of the graph")
    print("eg. a = AsciiGraph('x**3 - 10*x**2 + 5*x - 20',[-10,10,-1000,1000],30,2)")
    print("Give inputs to see the class in action")
    eq = get_user_equation()
    print("Python equation is " + eq)
    axes_range = get_user_range()
    dim = get_user_dim()
    print("Graph range is X from "+str(axes_range[0])+" to "+str(axes_range[1])+" and Y from "+str(axes_range[2])+" to "+str(axes_range[3]))
    print("For these inputs you would use:")
    print("a = AsciiGraph('"+eq+"',"+str(axes_range)+","+str(dim)+",2)")
    print("Everything is calculated on creating the instance of AsciiGraph")
    a = AsciiGraph(eq,axes_range,dim,2)
    print("Now that it has been created, we can call its save() method to create a .txt file")
    print("Use a.save(folder,filename)")
    folder = get_user_folder()
    filename = input("Enter a filename (without the .txt extension)")
    print("For this input you would use:")
    print("a.save('"+folder+"','"+filename+"')")
    a.save(folder,filename)
    print("Calling this method has created the textfile, go find it!")
    print()
    print()
    print()
    return None

#Allow code to run if this module is run directly, but don't run if imported...
if __name__ == "__main__":
    while True:
        demo()