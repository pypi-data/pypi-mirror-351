import unittest
from tamilstring.utf8 import get_letters, split_letter , make_letter ,unmatch_indeces, is_composite ,is_vowel ,is_consonent 


class TestBaseWord(unittest.TestCase):
    def test_get_letters(self):
        self.assertEqual(['த','மி','ழ்'],get_letters("தமிழ்"))
        self.assertNotEqual(['த','மி','ழ'],get_letters("தமிழ்"))
        self.assertEqual(['க்ஷி','க்ஷு'],get_letters("க்ஷிக்ஷு"))
        self.assertEqual(['௵'],get_letters("௵"))
        self.assertEqual(['ஶ்ரீ'],get_letters("ஶ்ரீ")) 
        self.assertEqual(['ஶ்ரீ','னி'],get_letters("ஶ்ரீனி")) 
    
    def get_unmatch_indeces(self):
        print(unmatch_indeces("தைைமிாாழ்்"))

    def remove_wrong_unicode(self):
        self.assertEqual(['த','மி','ழ்'],get_letters("தமிழ்்"))
        self.assertEqual([],get_letters("்ா")) 
        self.assertEqual(['க்ஷி','க்ஷு'],get_letters("க்ஷி்ாக்ஷு"))

    def test_split (self):
        self.assertEqual(('ம்','ஆ'),split_letter("மா"))
        self.assertEqual(('க்','ஓ'),split_letter("கோ"))
        self.assertEqual(('ண்','ஐ'),split_letter("ணை"))
        self.assertEqual((None,None),split_letter("ழ்"))
        self.assertEqual((None,None),split_letter("ஃ"))
        self.assertEqual((None,None),split_letter("௵"))
        self.assertEqual(("க்ஷ்","இ"),split_letter("க்ஷி")) 
        self.assertEqual(('ஶ்', 'அ'),split_letter("ஶ"))
        self.assertEqual(('க்ஷ்', 'ஐ'),split_letter("க்ஷை"))

    def test_make (self):
        self.assertEqual('ழௌ',make_letter("ழ்","ஔ"))
        self.assertEqual('பூ',make_letter("ப்","ஊ"))
        self.assertEqual('கை',make_letter("க்","ஐ"))
        self.assertEqual('மூ',make_letter("ம்","ஊ"))
        self.assertEqual('சா',make_letter("ச்","ஆ"))
        self.assertEqual(None,make_letter("ப்ப","ப்"))        
        self.assertEqual(None,make_letter("ச","ஆ"))
        self.assertEqual(None,make_letter("ப்","ப"))
        self.assertEqual(None,make_letter("ப்","ப்"))
        

    def test_is_vowel (self):
        self.assertTrue(is_vowel("அ"))
        self.assertTrue(is_vowel("ஔ"))
        self.assertTrue(is_vowel("ஓ"))
        self.assertTrue(is_vowel("இ"))
        self.assertFalse(is_vowel("a"))
        self.assertFalse(is_vowel("க்ஷ்"))
        self.assertFalse(is_vowel("௩"))
        self.assertFalse(is_vowel("௫"))
        self.assertNotEqual(True,is_vowel("ஃ"))
        self.assertNotEqual(True,is_vowel("க"))
        self.assertNotEqual(True,is_vowel("க்"))
        self.assertEqual(True,is_vowel("உ"))
        self.assertEqual(True,is_vowel("இ"))
           
 
    def test_is_consonent (self):
        self.assertTrue(is_consonent("க்"))
        self.assertTrue(is_consonent("ழ்"))
        self.assertTrue(is_consonent("க்ஷ்"))
        self.assertTrue(is_consonent("ஞ்"))
        self.assertFalse(is_consonent("a"))
        self.assertFalse(is_consonent("ஷி"))
        self.assertFalse(is_consonent("௩"))
        self.assertFalse(is_consonent("௫")) 
        self.assertNotEqual(True,is_consonent("ஃ"))
        self.assertNotEqual(True,is_consonent("அ"))
        self.assertEqual(True,is_consonent("க்"))
        self.assertEqual(True,is_consonent("ப்"))
            
   
    def test_is_composite (self):
        self.assertTrue(is_composite("க"))
        self.assertTrue(is_composite("ழ"))
        self.assertTrue(is_composite("க்ஷ"))
        self.assertTrue(is_composite("க்ஷூ"))
        self.assertFalse(is_composite("a"))
        self.assertFalse(is_composite("ஶ்"))
        self.assertFalse(is_composite("௩"))
        self.assertFalse(is_composite("௫"))
        self.assertNotEqual(True,is_composite("ஃ"))
        self.assertNotEqual(True,is_composite("அ"))
        self.assertEqual(True,is_composite("க"))
        self.assertEqual(True,is_composite("மா"))

