function filterPosts(a){
    document.getElementById('postsInput').value = a
}

function radioSpan(text, span){
    if (span === 'm'){
        document.getElementById('radio-span').innerHTML = text
    } else {
        document.getElementById(`radio-span${span}`).innerHTML = text
    }
}

async function like(event, action){
    let postId = action === 'like' ? event.target.id.slice(4) : event.target.id.slice(6)
    fetch('/likePost', {
        method: 'POST',
        body: JSON.stringify({
            id: postId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Liked"){
            document.querySelector(`#like${postId}`).classList.add('no-display');
            document.querySelector(`#unlike${postId}`).classList.remove('no-display');
            document.querySelector(`#unlike${postId}`).animate([
                {fontSize: "1.6rem", marginTop: "0.5em", marginBottom: "0.5em"}, // Font size == 1.6 ==> 0.5 em == 0.8 rem, total height == 3.2rem
                {fontSize: "2rem", marginTop: "0.6rem", marginBottom: "0.6rem"}, // (3.2 - 2) / 2 = 0.6 rem 
                {fontSize: "1.6rem", marginTop: "0.5em", marginBottom: "0.5em"}], 500);
        } else {
            document.querySelector(`#like${postId}`).classList.remove('no-display');
            document.querySelector(`#unlike${postId}`).classList.add('no-display');
        }
        document.querySelector(`#likeCount${postId}`).innerHTML = data.likes;
    })
}

window.addEventListener('DOMContentLoaded', () => {
    // Correctly display like/unlike buttons when the page loads
    let ids = []
    document.querySelectorAll('.post').forEach(post => ids.push(post.id.slice(1)))
    fetch('/liked', {
        method: 'POST',
        body: JSON.stringify({
            ids: ids
        })
    })
    .then(response => response.json())
    .then(data => {
        for (id in data){
            if (data[id]){
                document.querySelector(`#like${id}`).classList.add('no-display');
                document.querySelector(`#unlike${id}`).classList.remove('no-display');
            }
        }
    })

    // Close all opened menus when the user clicks outside the menu
    document.querySelector('body').addEventListener('click', event => {
        if (!event.target.classList.contains('dots')){
            document.querySelectorAll('.options-buttons').forEach(menu => {
                menu.classList.remove('options-shown')
                if (!menu.classList.contains('options-hidden')){
                    menu.classList.add('options-hidden')
                }
            })
        }
    })

    // Correct cropping of profile pictures
    document.querySelectorAll('.post-profile-pic').forEach(pic => {
        if (pic.width > pic.height){
            pic.style.maxHeight = "3rem";
        } else {
            pic.style.maxHeight = "3rem";
        }
    })
});

function displayComments(event){
    let id = event.target.id.slice(2)
    if (document.getElementById(`c${id}`).classList.contains('no-display')){
        document.getElementById(`c${id}`).classList.remove('no-display')
    } else {
        document.getElementById(`c${id}`).classList.add('no-display')
    }
}

function options(event){
    let id = event.target.id.slice(3)
    if (document.getElementById(`optionButtons${id}`).classList.contains('options-hidden')){
        document.getElementById(`optionButtons${id}`).classList.remove('options-hidden')
        document.getElementById(`optionButtons${id}`).classList.add('options-shown')
    } else {
        document.getElementById(`optionButtons${id}`).classList.remove('options-shown')
        document.getElementById(`optionButtons${id}`).classList.add('options-hidden')
    }
}

function commentOptions(event){
    let pId = event.target.classList[1]
    let id = event.target.id.slice(4).concat(pId)
    if (document.getElementById(`commentOptionButtons${id}`).classList.contains('options-hidden')){
        document.getElementById(`commentOptionButtons${id}`).classList.remove('options-hidden')
        document.getElementById(`commentOptionButtons${id}`).classList.add('options-shown')
    } else {
        document.getElementById(`commentOptionButtons${id}`).classList.remove('options-shown')
        document.getElementById(`commentOptionButtons${id}`).classList.add('options-hidden')
    }
}

// Disable search button if input is empty
function searchButton(event){
    console.log(event.target.value.length)
    if (event.target.value.length > 0){
        document.getElementById('srch-btn').disabled = false;
    } else {
        document.getElementById('srch-btn').disabled = true;
    }
}

function editPost(event){
    event.target.parentElement.classList.remove('options-shown');
    event.target.parentElement.classList.add('options-hidden');
    let postId = event.target.parentElement.id.slice(13);
    let postTextDiv = document.querySelector(`#pt${postId}`);
    let text = postTextDiv.innerHTML;
    let priv = document.querySelector(`#pr${postId}`).className == "pr" ? true : false;
    postTextDiv.innerHTML = `<form class="form2" onsubmit="editPostSubmit(event)">
                                <div class="form2">
                                    <div>    
                                        <input type="radio" name="type" value="public" class="post-checkbox" id="radio-public" ${priv ? "" : "checked"} onclick="radioSpan('Privacy: public', ${postId})">    
                                        <input type="radio" name="type" value="followers" class="post-checkbox" id="radio-followers" ${priv ? "checked" : ""} onclick="radioSpan('Privacy: only to people you follow', ${postId})">
                                        <span class="radio-span" id="radio-span${postId}">Privacy: ${priv ? "only to people you follow" : "public"}</span>
                                    </div>
                                    <textarea name="text" id="post-text" rows="7">${text}</textarea>
                                    <button type="submit" class="post-submit">Submit</button>
                                </div>
                            </form>`
}

function editPostSubmit(event){
    event.preventDefault()
    let text = event.target.elements.text.value
    let type = event.target.elements.type.value == 'followers' ? true : false
    let id = event.path[1].id.slice(2)
    fetch('/editPost', {
        method: 'POST',
        body: JSON.stringify({
            id: id,
            private: type,
            text: text
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success){
            document.querySelector(`#pt${id}`).innerHTML = text;
            document.querySelector(`#pr${id}`).innerHTML = type ? "🔒" : "🌐";
        } else {
            document.querySelector(`#pt${id}`).innerHTML = `<h4> An error has occurred, refresh the page and try again.`
        }
    })
}