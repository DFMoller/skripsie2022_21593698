
mylist = [{
    'val': 5
},
{
    'val': 6
},
{
    'val': 5
}]

min_dict = min(mylist, key=lambda x:x['val'])
print(min_dict)