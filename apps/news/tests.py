from django.test import TestCase

# Create your tests here.


a = {'name': '老王', 'like': '贾宝玉'}

b = {'name': '老王', 'like': '贾宝玉'}

print(id(a))
print(id(b))
