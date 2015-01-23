import os 

#Get the number of subfolders in a directory
def fcount(path, map = {}):
  count = 0
  for f in os.listdir(path):
    child = os.path.join(path, f)
    if os.path.isdir(child):
      child_count = fcount(child, map)
      count += child_count + 1 # unless include self
  map[path] = count
  return count


def ImageLoader():

    path_to_caps=os.getcwd()+"/training_images" #os.getcwd() gets the current directory
    
    #map = {}
    #fc=fcount(path_to_caps,map) 
    #fc=4
    fc = raw_input('Object ID:  ')
    path=path_to_caps+"/obj"+str(fc) #get the path of the last inserted observation/object
    
    os.chdir(path)#cd to a dir
    
    files_in_dir= len([name for name in os.listdir('.') if os.path.isfile(name)]) #get the number of files in a directory
    
    return files_in_dir, fc

    
