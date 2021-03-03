from django.db import models


MENU_TYPE_LIST = ['ENTRY INPUT', 'OPTION SELECT', 'FREE ENTRY', 'DYNAMIC MENU']


class Menu(models.Model):
    menu_type = models.CharField(max_length=20, choices=list(map(lambda x: (x, x), MENU_TYPE_LIST)))
    label_en = models.CharField(max_length=256)
    label_sw = models.CharField(max_length=256)
    parent_menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='nodes', null=True)
