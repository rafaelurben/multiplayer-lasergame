from map import Map 


width = 4
height = 2

map = Map(width, height)

map.change_field(0, 1, 3)
map.change_field(0, 2, 2)




map.step()



m = map.map
for l in m:
    print(l)
