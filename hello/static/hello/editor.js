(function(docId, currentUser) {
    const editor = document.getElementById('editor');
    const typingIndicator = document.getElementById('typing-indicator');
    let isUpdating = false;
    const cursors = {};

    // Function to generate a unique color for each user
    function getColorForUser(username) {
        let hash = 0;
        for (let i = 0; i < username.length; i++) {
            hash = username.charCodeAt(i) + ((hash << 5) - hash);
        }
        return `hsl(${hash % 360}, 75%, 50%)`;
    }

    // Function to load the document content from the server
    function loadDocumentContent(docId) {
        fetch(`/documents/${docId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                editor.innerHTML = data.content || ''; // Set the editor's content
                console.log('Document content loaded:', data.content);
                setupAutosave(); // Initialize autosave after loading content
            })
            .catch(error => {
                console.error('Error loading document:', error);
            });
    }

    // WebSocket setup to handle real-time collaboration
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/documents/${docId}/`);

    // WebSocket open event - connection established
    socket.onopen = () => {
        console.log('WebSocket connection established');
    };

    // WebSocket message event - handle incoming updates
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.action === 'edit') {
            const { content, user, cursorPosition } = data;

            // Update editor content only if it's not being typed locally
            if (!isUpdating && editor.innerHTML !== content) {
                isUpdating = true;
                editor.innerHTML = content;
                isUpdating = false;
            }

            // Update cursor position for the user
            if (cursorPosition) {
                updateCursor(user, cursorPosition);
            }

            // Show typing indicator for the user
            showUserTypingIndicator(user);
        }
    };

    // WebSocket error event - handle connection errors
    socket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        alert('WebSocket connection failed. Please try refreshing the page.');
    };

    // WebSocket close event - handle disconnection
    socket.onclose = () => {
        console.warn('WebSocket connection closed');
    };

    // Event listener to send updates when the content changes
    editor.addEventListener('input', () => {
        if (!isUpdating) {
            const content = editor.innerHTML;
            const cursorPosition = getCursorPosition();
            socket.send(JSON.stringify({
                action: 'edit',
                content: content,
                cursorPosition: cursorPosition,
                user: currentUser,
            }));
        }
    });

    // Function to display a typing indicator for a user
    function showUserTypingIndicator(username) {
        const existingIndicator = document.querySelector(`.typing-notification[data-user="${username}"]`);
        if (existingIndicator) {
            clearTimeout(existingIndicator.dataset.timeoutId);
        } else {
            const userTyping = document.createElement('div');
            userTyping.innerText = `${username} is typing...`;
            userTyping.classList.add('typing-notification');
            userTyping.dataset.user = username;
            typingIndicator.appendChild(userTyping);
        }

        const timeoutId = setTimeout(() => {
            const indicator = document.querySelector(`.typing-notification[data-user="${username}"]`);
            if (indicator && typingIndicator.contains(indicator)) {
                typingIndicator.removeChild(indicator);
            }
        }, 2000);

        if (existingIndicator) {
            existingIndicator.dataset.timeoutId = timeoutId;
        }
    }

    // Function to get the current cursor position
    function getCursorPosition() {
        const selection = window.getSelection();
        if (!selection.rangeCount) return null;

        const range = selection.getRangeAt(0);
        const path = getNodePath(range.startContainer);
        const offset = range.startOffset;

        return { path, offset };
    }

    // Utility function to get the path of a node relative to the editor
    function getNodePath(node) {
        const path = [];
        while (node && node !== editor) {
            const index = Array.prototype.indexOf.call(node.parentNode.childNodes, node);
            path.unshift(index);
            node = node.parentNode;
        }
        return path;
    }

    // Utility function to get a node from its path
    function getNodeFromPath(path) {
        let node = editor;
        try {
            for (const index of path) {
                node = node.childNodes[index];
            }
            return node;
        } catch (error) {
            console.error('Invalid node path:', path, error);
            return null;
        }
    }

    // Function to update the cursor position of a specific user
    function updateCursor(username, position) {
        let cursor = cursors[username];
        if (!cursor) {
            cursor = document.createElement('div');
            cursor.className = 'user-cursor';
            cursor.style.backgroundColor = getColorForUser(username);
            editor.appendChild(cursor);
            cursors[username] = cursor;
        }

        const node = getNodeFromPath(position.path);
        if (!node) return;

        const range = document.createRange();
        range.setStart(node, position.offset);

        const rect = range.getBoundingClientRect();
        const editorRect = editor.getBoundingClientRect();

        cursor.style.position = 'absolute';
        cursor.style.left = `${rect.left - editorRect.left}px`;
        cursor.style.top = `${rect.top - editorRect.top}px`;
        cursor.style.width = '2px';
        cursor.style.height = '1em';
        cursor.style.backgroundColor = getColorForUser(username);
        cursor.style.zIndex = '1000';
    }

    // Function to load and initialize the document
    loadDocumentContent(docId);

    // Function to format text in the editor
    function formatText(command) {
        document.execCommand(command, false, null);
    }

    // Function to search and replace text in the editor
    function searchAndReplace() {
        const searchText = document.getElementById('searchText').value;
        const replaceText = document.getElementById('replaceText').value;
        if (searchText === '') return;

        const content = editor.innerHTML;
        const regex = new RegExp(searchText, 'g');
        const newContent = content.replace(regex, replaceText);

        editor.innerHTML = newContent;
    }

    // Utility function to get CSRF token for AJAX requests
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return null;
    }

    // Function to download the file in a specified format
    function downloadFile() {
        const content = editor.innerHTML;
        const downloadType = document.getElementById('downloadType').value;
        let blob;
        let filename = `document.${downloadType}`;

        if (downloadType === 'html') {
            blob = new Blob([content], { type: 'text/html' });
        } else if (downloadType === 'txt') {
            const textContent = editor.innerText;
            blob = new Blob([textContent], { type: 'text/plain' });
        } else if (downloadType === 'doc') {
            blob = new Blob([content], { type: 'application/msword' });
        } else {
            alert('Unsupported download type.');
            return;
        }

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Placeholder function for duplicating a line
    function duplicateLine() {
        alert('Duplicate line functionality is not implemented yet.');
    }

    // Function to autosave the document content
    function autosaveDocument() {
        console.log('Autosave function called');
        const content = editor.innerHTML;
        console.log('Autosaving content:', content);
        fetch(`/documents/${docId}/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ content: content }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Document autosaved successfully.');
            } else {
                console.error('Autosave failed:', data.message);
            }
        })
        .catch(error => {
            console.error('Error during autosave:', error);
        });
    }

    // Function to set up periodic autosave
    function setupAutosave() {
        setInterval(autosaveDocument, 10000); // Autosave every 10 seconds

        let autosaveTimeout;
        editor.addEventListener('input', () => {
            if (autosaveTimeout) clearTimeout(autosaveTimeout);
            autosaveTimeout = setTimeout(autosaveDocument, 5000); // 5 seconds after last input
        });
    }

    // Expose utility functions globally for use in UI
    window.formatText = formatText;
    window.searchAndReplace = searchAndReplace;
    window.downloadFile = downloadFile;
    window.duplicateLine = duplicateLine;

})(window.docId, window.currentUser); // Pass docId and currentUser into the IIFE
