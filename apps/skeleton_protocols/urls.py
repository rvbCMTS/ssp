from django.urls import path
from .views import skeleton_protocols, skeleton_protocols_results, pex, pex_read, history, list_exams, exams, tree_grid


app_name = 'skeleton_protocols'
urlpatterns = [
    path('', skeleton_protocols, name='sp-results'),
    path('protocols', skeleton_protocols_results, name='sp-results-list'),
    path('history', history, name='sp-history'),
    path('list_exams', list_exams, name='sp-list-exams'),
    path('exams', exams, name='sp-exams'),
    path('pex', pex, name='sp-pex'),
    path('pex_read', pex_read, name='sp-pex-read'),
    path('TreeGrid', tree_grid)
]


