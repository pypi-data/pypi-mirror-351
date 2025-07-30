class My_List(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self):
        print('My_List.__iter__')
        return My_List_Iterator(super().__iter__())

class My_List_Iterator:

    def __init__(self, iterator):
        self.iterator = iterator
        
    def __next__(self):
        value = next(self.iterator)
        print('My_List_Iterator.__next__:', value)
        return value
    
print( sum(My_List([1,2,3])) )
