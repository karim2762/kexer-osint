function startScan(username){

const terminal = document.getElementById("terminal")
const bar = document.getElementById("bar")

let checked = 0
const total = 200

const source = new EventSource("/stream?username=" + username)

source.onmessage = function(event){

const data = JSON.parse(event.data)

checked++

let percent = (checked / total) * 100
bar.style.width = percent + "%"

const row = document.createElement("div")

if(data.status === "FOUND"){
row.className = "found"
row.innerHTML = "✔ " + data.site + " → <a href='"+data.url+"' target='_blank'>Profile</a>"
}
else{
row.className = "notfound"
row.innerText = "✖ " + data.site
}

terminal.appendChild(row)

}
}
