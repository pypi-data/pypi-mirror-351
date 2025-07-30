from . import utf8 


class Letter:

    _instance = None  
    
    def __new__(cls, *args, **kwargs):
        singleton = kwargs.pop('singleton', False)
        if singleton:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = True
            return cls._instance
        else: 
            return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        if not getattr(self, '_initialized', True):
            super().__init__(*args, **kwargs)
            self._initialized = True 
        if len(args) == 1:
            args1 = args[0]
            if isinstance(args1, str):
                args1 = str(args1)
            self.unicode = utf8.get_letters(args1)[0]
        else:
            self.unicode = None
        self.output = kwargs.pop('obj', False)
        
    def __add__(self,other):
        if not isinstance(other,Letter):
            other_letters =  utf8.get_letters(other)
          
            if len(other_letters) != 1: 
                other = String(other)
            else:
                other = Letter(other)
         
        if not isinstance(other, Letter):
            if self.is_consonent and other.singleton(0).is_vowel:
                return utf8.make_letter(self.letter,other.singleton(0).letter) + other[1:]
            else:
                return self.letter+ other.string
        
        if self.is_consonent and other.is_vowel: 
            return utf8.make_letter(self.letter,other.letter)
        else: 
            return self.letter + other.letter
            
    def __sub__(self, other):
        if  not isinstance(other,Letter):
            other_ =  utf8.get_letters(other)
            if len(other_) != 1:
                raise ValueError("only tamil letter can be modify.")
            else:
                other = Letter(other)
        if self.is_composite:
            if other.is_consonent or other.is_vowel:
                if other.is_vowel:
                    return Letter(self.consonent) if self.output else self.consonent
                elif other.is_consonent:
                    return Letter(self.vowel)  if self.output else self.vowel 
            else:
                raise ValueError("voule or constant can subract only from compound")     
        else:
            raise ValueError("non compound kind can not subractable")

    def __contains__(self, item):
        if item == self.letter:
            return True
        else:
            return False

    def __str__(self):
        return self.letter
 
    @property
    def string(self): 
        return self.unicode

    @string.setter
    def string(self, value):
        if value != None:
            self.unicode = value
        else:
            self.unicode = None 

    @property
    def kind(self):
        if self.is_vowel:
            return "VOL"
        elif self.is_consonent:
            return "CON"
        elif self.is_composite:
            return "COM"

    @property
    def letter(self):
        return self.unicode

    @letter.setter
    def letter(self, value):
        if value != None:
            self.unicode = value
        else:
            self.unicode = None 

    @property
    def is_vowel(self):
        if utf8.is_vowel(self.letter):
            return True
        else:
            return False
        
    @property
    def is_consonent(self):
        if utf8.is_consonent(self.letter):
            return True
        else:
            return False
        
    @property
    def is_composite(self): 
        if utf8.is_composite(self.letter):
            return True
        else:
            return False
    

    @property
    def vowel(self):
        if utf8.is_vowel(self.letter):
            return self.letter
        elif utf8.is_composite(self.letter):
            constant_ , vowel_ = utf8.split_letter(self.letter)
            return vowel_
        else:
            return None
    
    @vowel.setter
    def vowel(self, value):
        if utf8.is_vowel(value):
            #if utf8.is_vowel(self.letter):
            #    self.unicode = value
            if utf8.is_composite(self.letter):
                constant_ , vowel = utf8.split_letter(self.letter)
                self.unicode = utf8.make_letter(value,constant_)
            elif utf8.is_consonent(self.letter):
                self.unicode = utf8.make_letter(value,constant_)
            else:
                self.unicode = value
        
    @property
    def consonent(self):
        if utf8.is_consonent(self.letter):
            return self.letter
        elif utf8.is_composite(self.letter):
            constant_ , vowel_ = utf8.split_letter(self.letter)
            return constant_
        else:
            return None

    @consonent.setter
    def consonent(self, value):
        if utf8.is_consonent(value):
            if utf8.is_vowel(self.letter):
                self.unicode = utf8.make_letter(value,self.unicode)
            if utf8.is_composite(self.letter):
                constant_ , vowel_ = utf8.split_letter(self.letter)
                self.unicode = utf8.make_letter(value,vowel_)
            #elif utf8.is_consonent(self.letter):
            #    self.unicode = utf8.make_letter(value,constant_)
            else:
                self.unicode = value
        

    @property
    def composite(self):
        if utf8.is_composite(self.letter):
            return self.letter
        else:
            return None

    @composite.setter
    def composite(self, value):
        if utf8.is_composite(value):
            self.unicode = value
    
    def remove(self,kind):
        if self.is_composite:
            constant_ , vowel_ = utf8.split_letter(self.letter)
            if kind == "VOL":
                self.unicode = constant_
            elif kind == "CON":
                self.unicode = vowel_

    @property
    def split_letter(self):
        return utf8.split_letter(self.letter)
    
    def is_contains(self, other):
        if len(other) > 2:
            raise ValueError("it does not look like a seperate letter")
        if not isinstance(other, Letter):
            other = Letter(other)
        if other.letter == self.letter:
            return True
        elif (other.is_composite and not self.is_composite):
            return None
        elif (self.is_composite and not other.is_composite) :
            if other.letter in self.split_letter:
                return True
            else:
                return False

    def get_match(self, other, output=False):
        if not isinstance(other,Letter):
            other = Letter(other)
        output_value = (False,None) 
        if self.letter == other.letter:
            output_value = (True,other.kind)
        elif (other.is_composite and not self.is_composite):
            if self.letter in other.split_letter[0]:
                output_value = (True,other.kind)
        elif (self.is_composite and not other.is_composite):
            if other.letter == self.split_letter[1]:
                output_value = (True,other.kind)
        if output:
            return output_value
        else:
            return output_value[0]


class String:       
    _instance = None  

    def __new__(cls, *args, **kwargs):
        singleton = kwargs.pop('singleton', False)
        if singleton:
            if cls._instance is None:
                cls._instance = super(String, cls).__new__(cls)
                cls._instance._initialized = True 
            return cls._instance
        else:
            return super(String, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        if not getattr(self, '_initialized', True):
            super(String, self).__init__(*args, **kwargs)
            self._initialized = True 
        if len(args) > 0:
            args1 = args[0]
            if not isinstance(args1, str):
                args1 = str(args1)
            self.unicodes_list = utf8.get_letters(args1)
        else:
            self.unicodes_list = None
        self.output = kwargs.pop('object', False)
        self.position = 0
        self.inplace = kwargs.pop('inplace', False)

    def __add__(self,other):
        return_value = None
        if not isinstance(other,String):
            other = String(other)
        if self.singleton(-1).is_consonent and other.singleton(0).is_vowel:
            return_value = "".join(self.letters[:-1] + [utf8.make_letter(self.letters[-1],other.letters[0])] + other.letters[1:] )
        else:
            return_value = "".join(self.letters + other.letters)
        if self.output:
            return String(return_value)
        else:
            if self.inplace:
                pass
            else:
                return return_value

    def __sub__(self,other):
        return_value = None
        if not isinstance(other, Letter):
            other = Letter(other)
        if isinstance(other, Letter):
            if self.singleton(-1).is_composite and ( other.is_vowel or other.is_consonent): 
                final_letter = self.singleton(-1).consonent if other.kind == "VOL" else self.singleton(-1).vowel
                return_value = "".join( self.letters[:-1] ) + final_letter
            else:
                raise ValueError("can only subract string endings with voule or constant")        
        else:
            raise ValueError("can only subract string endings with voule or constant")

        if self.output:
            return String(return_value)
        else:
            if self.inplace:
                pass
            else:
                return return_value


    @property
    def letters(self):
        return self.unicodes_list
 
    @property
    def string(self):
        return "".join(self.unicodes_list)

    @string.setter
    def string(self,value):
        self.unicodes_list = utf8.get_letters(value)
       
    def has_contain(self, substring,):
        if isinstance(substring, String):
            subString = substring
        else:
            subString = String(substring)    
        matchValue, all_matches = [] ,[]       
        matchCount,tracer = 0,0
        letter = Letter('ஆ')
        for index , letter_ in enumerate(self.letters):
            letter.unicode = letter_
            if matchCount == len(subString.letters):
                subString.position,matchCount= 0,0
                all_matches.append((True,matchValue)) 
                matchValue = []
                tracer = index
            checkMatch =  letter.get_match(subString[subString.position],output=True )
            if checkMatch[0]:
                if self.letters[index] == subString[subString.position]: 
                    matchValue.append(letter_)
                    subString.position += 1 
                    matchCount += 1
                else:
                    constant,voule = letter.split_letter
                    if checkMatch[1] == "VOL":                       
                        matchValue.append(voule)
                        if len(all_matches) != 0:
                            if all_matches[-1][0] == True:
                                all_matches.append((False,constant))
                            else:
                                all_matches[-1] = (False,all_matches[-1][0]+[constant])
                        subString.position += 1  
                        matchCount += 1 
            else:
                if index == tracer:
                    all_matches.append( (False,[l for l in self.letters[tracer:index+1]]) )
                else:
                    all_matches[-1] = (False,[l for l in self.letters[tracer:index+1]])
            self.position = index
        return [(am[0],"".join(am[1]) ) for am in all_matches ]
         
    def object(self,index):
        return Letter(self.letters[index])

    def singleton(self,index):
        return Letter(self.letters[index],singleton = True)
     
    def __getitem__(self, index):
        return_value = None
        if isinstance(index, slice):
            if self.string:
                return_value = "".join(self.letters[index.start:index.stop:index.step])
            else:
                return_value = "".join(self.letters[index.start:index.stop:index.step])
        else:
            return_value = self.letters[index]

        if self.output:
            return String(return_value)
        else:
            if self.inplace:
                pass
            else:
                return return_value

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            start, stop, step =  index.indices(len(self.letters))   
            previous_value = self.letters
            if not isinstance(value, String):
                other = String(value,singleton = True)
            previous_value[start:stop:step] = other.letters
            self.string = "".join(previous_value)   
        else:
            previous_value = self.letters 
            previous_value[index] = value
            self.string = "".join(previous_value)  
           
    def __delattr__(self):
        del self

    def __iter__(self):
        return iter(self.letters)
    
    def __len__(self):
        return len(self.letters)

    def __contains__(self, other):        
        if not isinstance(other,str):
            other = str(other)
        if self. unicodes_list in other:
            return True
        else:
            return False

 