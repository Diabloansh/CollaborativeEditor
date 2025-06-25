from django.db import models
from django.contrib.auth.models import User

# Model to represent a document
class Document(models.Model):
    # Title of the document
    title = models.CharField(max_length=255)

    # Content of the document (text field for longer inputs)
    content = models.TextField()

    # The owner of the document (one-to-many relationship with User)
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # Delete the document if the owner is deleted
        related_name='owned_documents'  # Allows reverse access from User to owned documents
    )

    # Users with whom the document is shared (many-to-many relationship with User)
    shared_with = models.ManyToManyField(
        User, 
        related_name='shared_documents',  # Allows reverse access to shared documents
        blank=True  # Allows the field to be empty
    )

    # Timestamp for when the document was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Timestamp for when the document was last updated
    updated_at = models.DateTimeField(auto_now=True)

    # The last user who edited the document
    last_editor = models.ForeignKey(
        User, 
        null=True, 
        blank=True,  # Allows the field to be empty if no editor is set
        on_delete=models.SET_NULL,  # Keeps the document if the editor is deleted
        related_name="edited_documents"  # Allows reverse access from User to edited documents
    )

    # Indicates if the document is active (can be used for soft deletion or version control)
    is_active = models.BooleanField(default=False)

    # String representation of the model
    def __str__(self):
        return self.title


# Model to represent a version of a document
class DocumentVersion(models.Model):
    # The document to which this version belongs (one-to-many relationship)
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE,  # Delete all versions if the document is deleted
        related_name='versions'  # Allows reverse access to versions of a document
    )

    # Content of this version of the document
    content = models.TextField()

    # Timestamp for when this version was created
    timestamp = models.DateTimeField(auto_now_add=True)

    # The user who edited and created this version
    editor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Keeps the version if the editor is deleted
        null=True, 
        blank=True  # Allows the field to be empty
    )

    # String representation of the model
    def __str__(self):
        return f"{self.document.title} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} by {self.editor}"
