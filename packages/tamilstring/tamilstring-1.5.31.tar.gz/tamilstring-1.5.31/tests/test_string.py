import unittest
from tamilstring import Letter,String,get_letters


class TestBaseWord(unittest.TestCase):

    def test_singelton(self):
        l1 = String("க்",singleton = True)
        l2 = String("வா",singleton = True)
        self.assertEqual(id(l1),id(l2))

    def test_add_str(self):
        self.assertEqual("மெய்ம்மயக்கம", String("மெய்ம்மயக்கம்") + "அ" ) 
        self.assertEqual("மெய்ம்மயக்கம", String("மெய்ம்மயக்கம்") + String("அ") )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்ம்") + "அயக்கம்" )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்ம்") + String("அயக்கம்") )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்") + "மயக்கம்")
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்") + String("மயக்கம்") )
        self.assertEqual("மெய்ம்மயக்கம்மயக்கம்", String("மெய்ம்") + "மயக்கம்"+ "மயக்கம்")
     
    def test_add_obj(self):
        self.assertEqual("மெய்ம்மயக்கம", String("மெய்ம்மயக்கம்") + "அ" )  
        self.assertEqual("மெய்ம்மயக்கம", String("மெய்ம்மயக்கம்") + String("அ") )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்ம்") + "அயக்கம்" )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்ம்") + String("அயக்கம்") )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்") + "மயக்கம்" )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்") + String("மயக்கம்") )
    
    def test_subraction_single_letter(self):        
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்மயக்கம") - "அ" )
        self.assertEqual("மெய்ம்மயக்கம்", String("மெய்ம்மயக்கம") - Letter("அ") )
        self.assertEqual("மெய்ம்மயக்கஅ", String("மெய்ம்மயக்கம") - "ம்" )
        self.assertEqual("மெய்ம்மயக்கஅ", String("மெய்ம்மயக்கம") - Letter("ம்") )

    def test_letters(self):
        test_string = String("தமிழ்")
        self.assertEqual(['த','மி','ழ்'],test_string.letters)
        test_string.string = "ஶ்ரீனி"
        self.assertEqual(['ஶ்ரீ','னி'],test_string.letters)

    def test_capsules(self):
        actual_input = "தமிழ்"
        test_string = String(actual_input)
        test_string_get_letters = get_letters(actual_input)
        self.assertEqual(test_string_get_letters,test_string.letters)
        actual_input = "ஶ்ரீனி"
        test_string = String(actual_input)
        test_string_get_letters = get_letters(actual_input)

    def test_capsules(self):
        actual_input = "தமிழ்"
        test_string = String(actual_input)
        self.assertEqual("தமிழ்",test_string.string)
        test_string.string = "ஶ்ரீனி"
        self.assertEqual("ஶ்ரீனி",test_string.string)
        
    def test_singleton(self):
        actual_input = "தமிழ்"
        test_string = String(actual_input)
        letter1 = Letter("க்",singleton = True)
        self.assertEqual(id(letter1),id(test_string.singleton(0)))
        test_string.string = "ஶ்ரீனி"
        letter1 = Letter("க்",singleton = True)
        self.assertEqual(id(letter1),id(test_string.singleton(0)))
        
    def test_string_slicing(self): 
        word = String("மெய்ம்மயக்கம்")
        self.assertEqual("மெய்ம்", word[0:3] )
        self.assertEqual("ம்", word[2] )
        self.assertEqual("ம்", word[-1] )
        self.assertEqual("மய", word[3:5] )
        self.assertEqual("ம்கக்யமம்ய்மெ", word[::-1])
    
    def test_string_setter(self): 
        word = String("தழ்ழ்")
        word[1] = "மி"
        self.assertEqual("தமிழ்", word.string)
        word = String("தமிழ்")
        word[0:1] = "செந்த"
        self.assertEqual("செந்தமிழ்", word.string )
       
    def test_contains(self):
        self.assertTrue("த" in 'தமிழ்')
        self.assertTrue("வேண்டும்" in "என்னயென்னவேண்டும்")
        self.assertFalse("தி" in 'தமிழ்')

    def test_has_contains(self):
        String("என்னயென்னவேண்டும்").has_contain("என்ன")
