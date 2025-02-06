from scipy.spatial import distance
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
from dronekit import connect
import sys

N=list()
N.append(int(raw_input("Enter the number of UAVs: ")))

N.append(int(raw_input("Enter UAV which will remain in front: ")))

N.append(int(raw_input("Enter the minimum distance between UAVs(in metres): ")))

fig = plt.figure()
ax = fig.add_subplot(111)
#axis dimensions
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])

#uav_list 
uavs=[]
di = list()#np.zeros((N,N))
#generate meshgrid  
x=np.array([x for _ in range(0,10) for x in range(0,11)])
y=np.array([y for y in range(0,10) for _ in range(0,11)])

#pack x,y in one list 
x_y=np.array(list(zip(x,y)))
# plot scatter plot of mesh grid 
plt.scatter(x,y)

# plot the closest of the button click point
def plot_closest_pts(x,y):
    ind=distance.cdist([[x,y]],x_y,'euclidean').argmin()

    #prevent duplicate points
    uavs.append(tuple(x_y[ind]))
    if len(uavs)!=len(set(uavs)):
        uavs.pop(len(uavs)-1)

    plt.plot(x_y[ind][0], x_y[ind][1], color='red', marker='o', markersize=9)


# function to be followed on every button click
def onclick(event):
    #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %          (event.button, event.x, event.y, event.xdata, event.ydata))

    plot_closest_pts(event.xdata,event.ydata)
    #plt.plot(event.xdata, event.ydata, color='green', marker='o', markersize=9)

    #unzip x_y
    temp_x,temp_y=zip(*uavs)
    plt.plot(temp_x,temp_y)


    print("uavs",uavs)
    # distance matrix
    
    print("Distance matrix:n",di)
    #print("n")
    fig.canvas.draw()


cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()

d=distance.cdist(uavs, uavs, 'euclidean')
print d

'''
vehicle=connect('127.0.0.1:14550')

cmds=vehicle.commands
cmds.download()
cmds.wait_ready()

wp_temp=list()
waypoint_list=list()
for cmd in cmds:
    wp_temp.append(cmd.x)
    wp_temp.append(cmd.y)
    waypoint_list.append(wp_temp)

waypoint_list.pop(0)
print(waypoint_list)
'''

wp_list = list()

filename = str(sys.argv[1])
with open(filename) as content:
    lines = content.readlines()
    
string_list = list()    
for string in lines:
    x = string.split("\t")
    string_list.append(x)

#Remove first two items as junk
string_list.pop(0)
string_list.pop(0)

for i in string_list:
    wp_list.append([float(i[8]),float(i[9])])

#wp_list.append([1,1])
print(wp_list)


file=open("weight_matrix",'wb')
file2=open("number_of_UAVs",'wb')
file3=open("wp_list",'wb')
pickle.dump(d,file)
pickle.dump(N,file2)
pickle.dump(wp_list,file3)

file.close()
file2.close()
file3.close()

cmd=list()




