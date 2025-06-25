// Global Theme Toggle
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const currentTheme = localStorage.getItem('theme') || 'dark'; // Default to dark theme

    // Apply the current theme based on saved preference
    if (currentTheme === 'light') {
        body.classList.add('light-theme'); // Apply light theme
        updateToggleIcon('light');
    } else {
        body.classList.remove('light-theme'); // Keep dark theme as default
        updateToggleIcon('dark');
    }

    // Add event listener for the theme toggle button
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('light-theme'); // Toggle between themes
            let theme = 'dark';
            if (body.classList.contains('light-theme')) {
                theme = 'light';
            }
            localStorage.setItem('theme', theme); // Save the preference to local storage
            updateToggleIcon(theme); // Update the icon accordingly
        });
    }

    // Updates the theme toggle icon and tooltip based on the current theme
    function updateToggleIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'light') {
            icon.classList.remove('bi-moon-stars');
            icon.classList.add('bi-sun');
            themeToggle.title = "Switch to Dark Theme";
        } else {
            icon.classList.remove('bi-sun');
            icon.classList.add('bi-moon-stars');
            themeToggle.title = "Switch to Light Theme";
        }
    }
});

// Alert Timeout
function setupAlertTimeout() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease'; // Smooth fade-out
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500); // Remove the alert after fading out
        }, 5000); // 5 seconds timeout for alerts
    });
}
document.addEventListener('DOMContentLoaded', setupAlertTimeout);

// CSRF Token Setup for AJAX
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value); // Return the CSRF token from cookies
        }
    }
    return null; // Return null if no CSRF token is found
}

// AJAX Request Wrapper
async function sendRequest(url, method = 'GET', body = null) {
    const headers = {
        'X-CSRFToken': getCSRFToken(), // Add CSRF token for security
        'Content-Type': 'application/json', // Specify JSON format
    };
    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body); // Add request body if provided
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json(); // Parse and return JSON response
    } catch (error) {
        console.error('Error with AJAX request:', error);
    }
}

// Document Deletion Functionality
async function deleteDocument(docId, deleteUrl) {
    if (confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        const response = await sendRequest(deleteUrl, 'POST');
        if (response && response.status === 'success') {
            alert('Document deleted successfully.');
            location.reload(); // Reload the page to reflect changes
        } else {
            alert('An error occurred while deleting the document.');
        }
    }
}

// Setup delete buttons to handle document deletion
function setupDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-document-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const docId = button.dataset.docId; // Get document ID
            const deleteUrl = button.dataset.deleteUrl; // Get URL for deletion
            deleteDocument(docId, deleteUrl);
        });
    });
}
document.addEventListener('DOMContentLoaded', setupDeleteButtons);

// Text formatting using document.execCommand
function formatText(command) {
    document.execCommand(command, false, null); // Executes formatting command (e.g., bold, italic)
}

// Search and replace text in the editor
function searchAndReplace() {
    const searchText = document.getElementById('searchText').value; // Get text to search
    const replaceText = document.getElementById('replaceText').value; // Get replacement text
    const editor = document.getElementById('editor');
    if (editor) {
        const regex = new RegExp(searchText, 'g'); // Create regex for global search
        editor.innerHTML = editor.innerHTML.replace(regex, replaceText); // Replace matches
    }
}

// Download file with content from the editor in specified format
function downloadFileAs(type) {
    const editorContent = document.getElementById('editor').innerHTML;
    let blob;
    let extension;

    switch (type) {
        case 'html':
            blob = new Blob([editorContent], { type: 'text/html' });
            extension = 'html';
            break;
        case 'txt':
            blob = new Blob([editorContent], { type: 'text/plain' });
            extension = 'txt';
            break;
        case 'doc':
            const docContent = `
                <!DOCTYPE html>
                <html>
                <head><meta charset="utf-8"><title>Document</title></head>
                <body>${editorContent}</body>
                </html>`;
            blob = new Blob(['\ufeff', docContent], { type: 'application/msword' });
            extension = 'doc';
            break;
        default:
            console.error('Unsupported file type');
            return;
    }

    // Create a download link and trigger the download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `document.${extension}`;
    link.click();
    URL.revokeObjectURL(link.href); // Clean up the object URL
}

// Setup download button functionality
document.addEventListener('DOMContentLoaded', () => {
    const downloadButton = document.getElementById('download-button');
    if (downloadButton) {
        downloadButton.addEventListener('click', () => {
            const downloadType = document.getElementById('downloadType').value; // Get selected format
            downloadFileAs(downloadType);
        });
    }
});

// Display typing indicator for collaborative editing
function showTypingIndicator(username) {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.textContent = `${username} is typing...`; // Show typing message
        setTimeout(() => {
            typingIndicator.textContent = ''; // Clear the message after 2 seconds
        }, 2000);
    }
}
