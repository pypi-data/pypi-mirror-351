const fileListElement = document.getElementById("file-list")

async function fetchFileList(name) {
    try {
        const searchParams = new URLSearchParams({name: name})
        const response = await fetch(`/api/files?${searchParams.toString()}`); // Replace with your API endpoint
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const fileList = await response.json();
        return fileList
    } catch (error) {
        console.error("Could not fetch file list:", error);
    }
}

async function displayFileList(base, files) {
    const body = document.body;
    fileListElement.innerHTML = "";
    files.forEach(async (file) => {
        const link = document.createElement("a");
        link.href="#"
        if (file.is_dir) {
            link.textContent = `[ dir  ] ${file.name}`
        } else {
            link.textContent = `[ file ] ${file.name}`;
        }
        link.addEventListener("click", async function(event) {
            event.preventDefault();
            const newBase = base + "/" + file.name
            if (file.is_dir) {
                const file_list = await fetchFileList(newBase);
                await displayFileList(newBase, file_list.files);
            } else {
                // download
                const searchParams = new URLSearchParams({name: newBase});
                window.open(`/api/download?${searchParams.toString()}`, '_blank');
            }
        });
        fileListElement.appendChild(link);
    });
}

async function init() {
    const fileList = await fetchFileList(".");
    await displayFileList(".", fileList.files);
}
// Fetch the file list when the page loads
window.onload = init;