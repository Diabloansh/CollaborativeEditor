import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Document, DocumentVersion
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShareDocumentForm

# Configure logging
logger = logging.getLogger(__name__)

# View for the index page, redirects to the document list if the user is authenticated
def index(request):
    if request.user.is_authenticated:
        return redirect('document_list')
    return render(request, 'hello/login.html')

# Handles login for the text editor
def text_editor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in and redirect to document list
            login(request, user)
            return redirect('document_list')
        else:
            # Display error message if authentication fails
            messages.error(request, "Invalid username or password.")
            return render(request, 'hello/login.html')
    else:
        return render(request, 'hello/login.html')

# Handles user registration
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validate input fields
        if not username or not password or not password_confirm:
            messages.error(request, "All fields are required.")
            return render(request, 'hello/signup.html')
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'hello/signup.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'hello/signup.html')
        
        # Create a new user account
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect('document_list')
    else:
        return render(request, 'hello/signup.html')

# Logs out the user
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('index')

# Displays a list of documents owned or shared with the user
@login_required
def document_list(request):
    owned_documents = Document.objects.filter(owner=request.user)
    shared_documents = Document.objects.filter(shared_with=request.user)
    context = {
        'owned_documents': owned_documents,
        'shared_documents': shared_documents
    }
    return render(request, 'hello/document_list.html', context)

# Allows the user to create a new document
@login_required
def create_document(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Document')
        # Create a new document
        document = Document.objects.create(title=title, content='', owner=request.user)
        return redirect('editor', doc_id=document.id)
    else:
        return render(request, 'hello/create_document.html')

# Editor view for editing a specific document
@login_required
def editor(request, doc_id):
    try:
        document = Document.objects.get(id=doc_id)
        if document.owner == request.user or request.user in document.shared_with.all():
            return render(request, 'hello/editor.html', {
                'doc_id': doc_id,
                'user': request.user,
                'title': document.title,
                'content': document.content,
            })
        else:
            messages.error(request, "You do not have permission to edit this document.")
            return redirect('document_list')
    except Document.DoesNotExist:
        messages.error(request, "Document not found.")
        return redirect('document_list')

# Save the document content
@login_required
def save_document(request, doc_id):
    if request.method == "POST":
        try:
            document = Document.objects.get(id=doc_id)
            if document.owner == request.user or request.user in document.shared_with.all():
                # Parse the request body as JSON
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError:
                    return JsonResponse({"status": "error", "message": "Invalid JSON data."}, status=400)
                
                # Update document content
                content = data.get("content", "")
                document.content = content
                document.last_editor = request.user 
                document.save()

                # Save a new version of the document
                DocumentVersion.objects.create(
                    document=document,
                    content=content,
                    editor=request.user
                )

                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error", "message": "You do not have permission to save this document."}, status=403)
        except Document.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Document not found."}, status=404)
    else:
        return JsonResponse({"status": "error", "message": "Method Not Allowed. Please use POST."}, status=405)

# Deletes a document owned by the user
@login_required
def delete_document(request, doc_id):
    if request.method == 'POST':
        try:
            document = Document.objects.get(id=doc_id, owner=request.user)
            document.delete()
            logger.debug(f"Document {doc_id} deleted by user {request.user.username}.")
            return JsonResponse({"status": "success"})
        except Document.DoesNotExist:
            logger.error(f"Attempt to delete non-existent or unauthorized document {doc_id} by user {request.user.username}.")
            return JsonResponse({"status": "error", "message": "Document not found or you do not have permission to delete it."}, status=404)
    else:
        logger.warning(f"Invalid method {request.method} used to access delete_document.")
        return JsonResponse({"status": "error", "message": "Method Not Allowed. Please use POST."}, status=405)

# Retrieve a document's content
def get_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    return JsonResponse({'id': document.id, 'content': document.content})

# Share a document with other users
@login_required
def share_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, owner=request.user)

    if request.method == 'POST':
        form = ShareDocumentForm(request.POST)
        form.fields['users'].queryset = User.objects.exclude(id=request.user.id)
        if form.is_valid():
            new_shared_users = form.cleaned_data['users']
            old_shared_users = document.shared_with.all()

            # Update shared users
            document.shared_with.set(new_shared_users)
            document.save()

            added_users = set(new_shared_users) - set(old_shared_users)
            removed_users = set(old_shared_users) - set(new_shared_users)

            # Display messages for changes in sharing
            if added_users:
                added_usernames = ', '.join(user.username for user in added_users)
                messages.success(request, f"Document shared with: {added_usernames}.")
            if removed_users:
                removed_usernames = ', '.join(user.username for user in removed_users)
                messages.info(request, f"Access revoked from: {removed_usernames}.")

            if not added_users and not removed_users:
                messages.info(request, "No changes made to document sharing.")

            return redirect('document_list')
        else:
            messages.error(request, 'Invalid data submitted.')
    else:
        form = ShareDocumentForm()
        form.fields['users'].queryset = User.objects.exclude(id=request.user.id)
        form.initial['users'] = document.shared_with.all()

    return render(request, 'hello/share_document.html', {'form': form, 'document': document})

# Displays version history for a document
@login_required
def version_history(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    if document.owner != request.user and request.user not in document.shared_with.all():
        messages.error(request, "You do not have permission to view the version history of this document.")
        return redirect('document_list')
    
    # Fetch versions ordered by timestamp (latest first)
    versions = document.versions.order_by('-timestamp')
    
    return render(request, 'hello/version_history.html', {
        'document': document,
        'versions': versions,
    })

# View a specific version of a document
@login_required
def view_version(request, doc_id, version_id):
    document = get_object_or_404(Document, id=doc_id)
    version = get_object_or_404(DocumentVersion, id=version_id, document=document)
    if document.owner != request.user and request.user not in document.shared_with.all():
        messages.error(request, "You do not have permission to view this version of the document.")
        return redirect('document_list')
    
    return render(request, 'hello/view_version.html', {
        'document': document,
        'version': version,
    })

# Revert a document to a specific version
@login_required
def revert_version(request, doc_id, version_id):
    document = get_object_or_404(Document, id=doc_id)
    version = get_object_or_404(DocumentVersion, id=version_id, document=document)
    if document.owner != request.user and request.user not in document.shared_with.all():
        messages.error(request, "You do not have permission to revert this document.")
        return redirect('document_list')
    
    if request.method == "POST":
        # Revert document content
        document.content = version.content
        document.last_editor = request.user
        document.save()

        # Save the reverted version as a new document version
        DocumentVersion.objects.create(
            document=document,
            content=version.content,
            editor=request.user
        )
        
        messages.success(request, "Document has been reverted to the selected version.")
        return redirect('editor', doc_id=document.id)
    else:
        return render(request, 'hello/revert_version.html', {
            'document': document,
            'version': version,
        })
