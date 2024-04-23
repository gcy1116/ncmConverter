document.getElementById('file-upload').addEventListener('change', function(e) {
    console.log("文件已选择", e.target.files);
    const fileListContainer = document.getElementById('file-list');
    fileListContainer.innerHTML = ''; // 清空现有列表
    Array.from(e.target.files).forEach((file, index) => {
        const listItem = document.createElement('li');
        listItem.textContent = file.name;

        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.addEventListener('click', function() {
            // 从列表中删除此项
            fileListContainer.removeChild(listItem);
            // 更新input file的value
            e.target.value = ''; // 重新设置文件选择器
        });

        listItem.appendChild(removeButton);
        fileListContainer.appendChild(listItem);
    });
});

// document.getElementById('convert-btn').addEventListener('click', function() {
//     const files = document.getElementById('file-upload').files;
//     const formData = new FormData();
//     for (let i = 0; i < files.length; i++) {
//         formData.append('files', files[i]);
//     }

//     fetch('/convert', {
//         method: 'POST',
//         body: formData,
//     })
//     .then(response => response.json())
//     .then(data => {
//         document.getElementById('download-btn').style.display = 'inline';
//         document.getElementById('download-btn').addEventListener('click', function() {
//             window.location.href = data.downloadUrl; // URL由服务器返回
//         });
//     })
//     .catch(error => console.error('Error:', error));
// });

document.getElementById('convert-btn').addEventListener('click', function() {
    if (document.getElementById('file-upload').files.length === 0) {
        alert('请选择文件');
        return;
    }
    const files = document.getElementById('file-upload').files;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    // 显示进度条并开始模拟进度
    const progress = document.getElementById('upload-progress');
    let progressValue = 0;
    progress.value = progressValue;

    const interval = setInterval(() => {
        progressValue += 3; // 每次增加1%直到95%
        if (progressValue <= 95) {
            progress.value = progressValue;
        } else {
            clearInterval(interval);
        }
    }, 100); // 调整间隔时间来控制加载速度

    fetch('/convert', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // 转换完成，立即将进度条设置为最大值
        clearInterval(interval);
        progress.value = 100;
        document.getElementById('download-btn').style.display = 'inline';
        document.getElementById('download-btn').addEventListener('click', function() {
            window.location.href = data.downloadUrl;
        });
    })
    .catch(error => {
        console.error('Error:', error);
        clearInterval(interval); // 清除定时器以防错误
    });
});

