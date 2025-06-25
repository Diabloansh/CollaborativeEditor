from django.urls import path
from . import views

# URL configuration for the application
urlpatterns = [
    # Root URL, redirects to the index view
    path('', views.index, name='index'),

    # URL for the login page, handled by the text_editor view
    path('login/', views.text_editor, name='text_editor'),

    # URL for the signup page, handled by the signup view
    path('signup/', views.signup, name='signup'),

    # URL to log out the user, handled by the logout_view
    path('logout/', views.logout_view, name='logout'),

    # URL to list all documents (owned and shared), handled by the document_list view
    path('documents/', views.document_list, name='document_list'),

    # URL to create a new document, handled by the create_document view
    path('documents/create/', views.create_document, name='create_document'),

    # URL to edit a specific document by its ID, handled by the editor view
    path('documents/<int:doc_id>/edit/', views.editor, name='editor'),

    # URL to save changes to a specific document by its ID, handled by the save_document view
    path('documents/<int:doc_id>/save/', views.save_document, name='save_document'),

    # URL to retrieve the content of a specific document by its ID, handled by the get_document view
    path('documents/<int:doc_id>/', views.get_document, name='get_document'),

    # URL to delete a specific document by its ID, handled by the delete_document view
    path('documents/<int:doc_id>/delete/', views.delete_document, name='delete_document'),

    # URL to share a specific document with other users, handled by the share_document view
    path('documents/<int:doc_id>/share/', views.share_document, name='share_document'),

    # URL to view the version history of a specific document, handled by the version_history view
    path('documents/<int:doc_id>/versions/', views.version_history, name='version_history'),

    # URL to view a specific version of a document, handled by the view_version view
    path('documents/<int:doc_id>/versions/<int:version_id>/view/', views.view_version, name='view_version'),

    # URL to revert a document to a specific version, handled by the revert_version view
    path('documents/<int:doc_id>/versions/<int:version_id>/revert/', views.revert_version, name='revert_version'),

    # Additional URL patterns can be added here as needed
]
