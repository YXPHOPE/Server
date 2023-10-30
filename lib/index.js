// 优化界面，添加文件操作选项，重命名，删除，下载（?token=）
var file = $("#file-container #root"),
  video = $("#video video"),
  track = $("#video video track"),
  audio = $("#audio audio"),
  image = $("#image img"),
  curfile = $("#curfile"),
  ifr = $("#iframe iframe"),
  pre = $("#text pre"),
  doc = $("#doc>div"),
  excel = $("#excel>div"),
  link = $("#link a"),
  astext = $("#astext"),
  show = $("#content"),
  // btns = $("#btns"),
  tips = $("#tips"),
  terminal = $("#terminal"),
  stdin = $("#stdin"),
  stdout = $("#stdout"),
  quick = $("#quick"),
  remove = $("#remove"),
  rmSVG = $("#rmSVG"),
  forchat = $("#forchat"),
  chat = $("#chat"),
  chatHist = $("#history"),
  chatVal = $("#send>textarea"),
  chatName = $("#chatName"),
  resizer = $("#resize"),
  filectn = $("#file-container"),
  musiclist = $("#musiclist"),
  fileheader = $("#file-head"),
  curpath = $('#curpath'),
  remote = $("#remote"),
  menu = $("#menu"),
  drop = $("#drop"),
  lrc = $("#lrc"),
  lrcs = $("#lrcs>div"),
  hstryStack = [0],
  docu = document.documentElement,
  wschat = {},
  drag,
  last,
  quicklists = JSON.parse(localStorage.quicklists || "[]"),
  mobile = !1,
  Tok,
  Mobile = "undefined" !== typeof window.orientation,
  UNIT = ["b", "Kb", "Mb", "Gb"],
  Alink = nE("a"),
  Folder = {},
  encURL = (s)=>{return encodeURIComponent(s).replace('%3A',':').replaceAll('%2F','/')},
  current = null,
  WH = [1920,1080],
  CHAT = { time: 0, ip: "", name: "蒙面大侠" };
Alink.style.cssText = "width:0;height:0;overflow:hidden;opacity:0";
Alink.setAttribute("download", "");
docu.append(Alink);
let PWD = 0; // localStorage.token;
Ehide(astext);

var Cookies = {
  getItem: function (sKey) {
    return decodeURIComponent(document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + encURL(sKey).replace(/[-.+*]/g, "\\$&") + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1")) || null;
  },
  setItem: function (sKey, sValue, vEnd, sPath, sDomain, bSecure) {
    if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) {
      return false;
    }
    var sExpires = "";
    if (vEnd) {
      switch (vEnd.constructor) {
        case Number:
          sExpires = vEnd === Infinity ? "; expires=Fri, 31 Dec 9999 23:59:59 GMT" : "; max-age=" + vEnd;
          break;
        case String:
          sExpires = "; expires=" + vEnd;
          break;
        case Date:
          sExpires = "; expires=" + vEnd.toUTCString();
          break;
      }
    }
    document.cookie = encURL(sKey) + "=" + encURL(sValue) + sExpires + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "") + (bSecure ? "; secure" : "");
    return true;
  },
  removeItem: function (sKey, sPath, sDomain) {
    if (!sKey || !this.hasItem(sKey)) {
      return false;
    }
    document.cookie = encURL(sKey) + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "");
    return true;
  },
};
Tok = Cookies.getItem("token");
const convert = (wb) => {
  const sheets = [];
  let maxLength = 0;
  let maxCols = 0;
  wb.SheetNames.forEach((name) => {
    const sheet = { name, rows: {} };
    const ws = wb.Sheets[name];
    const rows = XLSX.utils.sheet_to_json(ws, { raw: false, header: 1 });
    if (maxLength < rows.length) maxLength = rows.length;
    sheet.rows = rows.reduce((map, row, i) => {
      const cells = row.reduce((colMap, column, j) => {
        colMap[j] = { text: column };
        return colMap;
      }, {});
      map[i] = { cells };
      const colLen = Object.keys(cells).length;
      if (colLen > maxCols) {
        maxCols = colLen;
      }
      return map;
    }, {});
    sheets.push(sheet);
  });
  return { sheets, maxLength, maxCols };
};

let sheetIns = null;

function loadSheet(buffer, ext) {
  (async () => {
    const ab = new Uint8Array(buffer).buffer;
    const wb = ext.toLowerCase() == ".csv" ? XLSX.read(new TextDecoder("utf-8").decode(ab), { type: "string", raw: true }) : XLSX.read(ab, { type: "array" });
    var { sheets, maxLength, maxCols } = convert(wb);
    sheetIns =
      sheetIns ||
      x_spreadsheet(excel, {
        row: {
          len: maxLength + 20,
          height: 30,
        },
        col: {
          len: maxCols + 5,
        },
        style: {
          align: "center",
        },
      });
    sheetIns.loadData(sheets);
  })();
}

let extName = "xlsx",
  ext = ".xlsx";
function dataToSheet(xws) {
  var aoa = [[]];
  var rowobj = xws.rows;
  for (var ri = 0; ri < rowobj.len; ++ri) {
    var row = rowobj[ri];
    if (!row) continue;
    aoa[ri] = [];
    /* eslint-disable no-loop-func */
    Object.keys(row.cells).forEach(function (k) {
      var idx = +k;
      if (isNaN(idx)) return;
      aoa[ri][idx] = row.cells[k].text;
    });
  }
  return XLSX.utils.aoa_to_sheet(aoa);
}

function xtos(sdata) {
  var out = XLSX.utils.book_new();
  sdata.forEach(function (xws) {
    ws = dataToSheet(xws);
    XLSX.utils.book_append_sheet(out, ws, xws.name);
  });
  return out;
}

function export_xlsx() {
  if (["xlsx", "xls", "ods"].includes(extName)) {
    var new_wb = xtos(sheetIns.getData());
    var buffer = XLSX.write(new_wb, { bookType: extName, type: "array" });
    const array = [...new Uint8Array(buffer)];
    vscodeEvent.emit("save", array);
  } else if (extName == "csv") {
    const csvContent = XLSX.utils.sheet_to_csv(dataToSheet(sheetIns.getData()[0]));
    vscodeEvent.emit("saveCsv", csvContent);
  }
}
chatHist.src = stdout.src = "";
var dcsty = document.documentElement.style;
window.innerWidth <= 600 && ((mobile = !0), show.classList.add("mobile"), dcsty.setProperty("--left", "0%")), (last = video), (file.path = "");
dcsty.prev = dcsty.getPropertyValue("--left");
let lastPath = localStorage.lastPath || "/*",
  prevPath = "/*";
hstryStack.push(lastPath);
console.log(lastPath);
Get(lastPath, (r) => {
  (r = JSON.parse(r)), gendom(file, r, 1);
});
function $(s) {
  return document.querySelector(s);
}
function nE(e, id, cla, html = "") {
  var ele = document.createElement(e);
  return id && (ele.id = id), cla && (ele.className = cla), html && (ele.innerHTML = html), ele;
}
function Get(url = "/", callback, header) {
  let xhr = new XMLHttpRequest();
  if ((xhr.open("GET", url), header)) for (const i in header) xhr.setRequestHeader(i, header[i]);
  // xhr.setRequestHeader("token", PWD);
  xhr.timeout = 2000;
  (xhr.onload = () => {
    200 === xhr.status
      ? callback && callback(xhr.response)
      : 403 === xhr.status
      ? ((PWD = parseInt(prompt("Password")) ^ 0x66666666),
        runCmd({ oprt: "token", pwd: PWD }, (r) => {
          r = JSON.parse(r);
          if (r.token) {
            Tok = r.token;
            Cookies.setItem("token", r.token, 1800);
            pushTip("Success");
            refresh();
          } else {
            pushTip("Error", r);
          }
        }))
      : pushTip("Error!", xhr.responseText);
  }),
    (xhr.onerror = () => {
      pushTip("Error", xhr.responseText);
    }),
    (xhr.ontimeout = () => {
      pushTip("Timeout", "");
    }),
    xhr.send();
}
function runCmd(cmd, callback, ret = !1, timeout = 3) {
  let xhr = new XMLHttpRequest();
  xhr.open("POST", "/"),
    xhr.setRequestHeader("Content-Type", "application/json"),
    // xhr.setRequestHeader("token", PWD),
    (xhr.onload = () => {
      400 === xhr.status ? pushTip("Error!", xhr.responseText) : callback && callback(xhr.responseText);
    }),
    (xhr.onerror = () => {
      pushTip("Error!", xhr.responseText);
    }),
    typeof cmd === "object" ? xhr.send(JSON.stringify(cmd)) : xhr.send(JSON.stringify({ oprt: "cmd", cmd: cmd, return: ret, timeout: timeout }));
}
function getLocal(filename, callback) {
  filename.indexOf("\\") >= 0 && (filename = filename.replaceAll("\\", "/"));
  let xhr = new XMLHttpRequest();
  xhr.open("POST", "/"),
    // xhr.setRequestHeader("token", PWD),
    xhr.setRequestHeader("Content-Type", "application/json"),
    (xhr.onload = () => {
      callback && callback(xhr);
    }),
    xhr.send(JSON.stringify({ oprt: "get", file: filename }));
}
/* file.addEventListener("contextmenu", (e) => {
  e.preventDefault();
  menu.style.left = e.clientX + "px";
  menu.style.top = e.clientY + "px";
  Eshow(menu);
  clearTimeout(menu.tmo);
  menu.tmo = setTimeout(() => {
    Ehide(menu);
  }, 4000);
  let ele = e.target;
  ele.className || (ele = ele.parentElement);
  file.querySelector(".sel") || ele.classList.add("sel");
  return false;
}); */
menu.addEventListener("click", (e) => {
  let o = e.target.getAttribute("for");
  let s = file.querySelectorAll(".sel");
  if (o === "rename") {
    //runCmd({oprt:'rename',path:''})
  } else if (o === "delete") {
    s.forEach((v) => {
      runCmd({ oprt: "delete", path: v.path.slice(1), type: v.folder ? "folder" : "file" });
    });
  } else if (o === "download") {
    s.forEach((v) => {
      Alink.href = v.path + Tok ? "?token=" + Tok : "";
      Alink.setAttribute("download", v.name);
      Alink.click();
    });
  } else if (o === "newfolder") {
  } else if (o === "newfile") {
  }
});
function renameout(e) {
  let fn = e.target;
  if (e.key === "Enter") {
    docu.focus();
    e.preventDefault();
    return false;
  } else if (!e.key) {
    fn.contentEditable = "false";
    let nm = fn.innerText;
    setTimeout(() => {
      file.rename = false;
    }, 300);
    let f = fn.parentElement;
    if (nm !== f.name) {
      fn.innerText = f.name;
      let np = f.path.slice(1, f.path.lastIndexOf("/") + 1) + nm;
      runCmd({ oprt: "rename", path: f.path.slice(1), name: np }, (r) => {
        fn.innerText = f.name = Folder.file[f.ind].name = nm;
        f.path = "/" + np;
      });
    }
    f.removeEventListener("focusout", renameout);
    f.removeEventListener("keydown", renameout);
  }
}
var lastDrag = filectn;
filectn.addEventListener("dragenter", (e) => {
  let t = e.target;
  if (!t.className) {
    t = t.parentElement;
  }
  e.stopPropagation();
  if (t === lastDrag) {
    return;
  }
  lastDrag.classList.remove("drop");
  if (t.folder) {
    t.classList.add("drop");
    lastDrag = t;
    drop.innerText = t.path.slice(1);
  } else {
    filectn.classList.add("drop");
    lastDrag = filectn;
    drop.innerText = file.path.slice(1);
  }
});
filectn.addEventListener("dragover", (e) => {
  e.stopPropagation();
  e.preventDefault();
});
filectn.addEventListener("drop", (e) => {
  const files = e.dataTransfer.files;
  let t = e.target;
  if (!t.className) {
    t = t.parentElement;
  }
  filectn.classList.remove("drop");
  e.preventDefault();
  for (let i = 0; i < files.length; i++) {
    Post((t.folder ? t.path : file.path) + files[i].name, files[i]);
  }
});
// 当drag时，不会触发mouseout等事件，无用
filectn.addEventListener("mouseout", () => {
  lastDrag.classList.remove("drop");
  filectn.classList.remove("drop");
});
file.addEventListener("click", (e) => {
  let ele = e.target;
  Ehide(menu);
  ele.className || (ele = ele.parentElement);
  if (e.shiftKey) {
    getSelection().removeAllRanges();
    let s = file.querySelectorAll(".sel");
    if (!s) {
      ele.classList.add("sel");
    } else {
      s = s[s.length - 1];
      if ((s.folder && ele.file) || (s.folder && ele.folder && s.ind < ele.ind) || (s.file && ele.file && s.ind < ele.ind)) {
        while (s !== ele) {
          s = s.nextElementSibling;
          s.classList.add("sel");
        }
      } else {
        while (s !== ele) {
          s = s.previousElementSibling;
          s.classList.add("sel");
        }
      }
    }
  } else if (e.ctrlKey) {
    ele.classList.contains("sel") ? ele.classList.remove("sel") : ele.classList.add("sel");
  } else {
    file.querySelectorAll(".sel").forEach((v) => {
      v.classList.remove("sel");
    });
    if (file.rename) {
      return;
    }
    if (ele.folder)
      Get(ele.path, (r) => {
        (r = JSON.parse(r)), gendom(file, r, 1);
      });
    else if (ele.file) {
      openFile(ele);
    } else if (ele.classList.contains("but")) {
      let f = ele.parentElement.parentElement;
      if (ele.classList.contains("rename")) {
        let n = f.firstElementChild;
        n.contentEditable = "true";
        n.focus();
        file.rename = true;
        f.addEventListener("focusout", renameout);
        f.addEventListener("keydown", renameout);
      } else if (ele.classList.contains("delete")) {
        runCmd({ oprt: "delete", path: f.path.slice(1), type: f.folder ? "folder" : "file" }, (r) => {
          f.remove();
        });
      }
    }
  }
}),
  file.addEventListener("dragstart", (e) => {
    rmSVG.style.display = remove.style.display = "block";
    drag = e.target;
  }),
  file.addEventListener("dragend", () => {
    rmSVG.style.display = remove.style.display = "none";
  }),
  remove.addEventListener("dragenter", () => {
    remove.style.opacity = 0;
  }),
  remove.addEventListener("dragover", (e) => {
    e.preventDefault();
  }),
  remove.addEventListener("dragleave", () => {
    remove.style.opacity = 0.5;
  }),
  remove.addEventListener("drop", () => {
    rmSVG.style.display = remove.style.display = "none";
    let i = quicklists.indexOf(drag.path);
    if (i >= 0) {
      quicklists = quicklists.splice(i, i);
      localStorage.quicklists = JSON.stringify(quicklists);
      pushTip("Removed quickLink", drag.path);
    }
    drag.remove();
  }),
  $("#header").addEventListener("click", (e) => {
    let id = e.target.id;
    "toText" === id ? toggleType(pre) : "toImage" === id ? toggleType(image) : "toVideo" === id ? toggleType(video) : "toAudio" === id ? toggleType(audio) : "toIfram" === id && toggleType(ifr);
  }),
  $("#home").addEventListener("click", () => {
    Get("/*", (r) => {
      (r = JSON.parse(r)), gendom(file, r, 1);
    });
  });
fileheader.size = fileheader.date = 1;
fileheader.addEventListener("click", (e) => {
  let t = e.target.innerHTML.slice(0, 4);
  if (t === "Name") {
    fileheader.name = !fileheader.name;
    fileheader.name
      ? Folder.file.sort((a, b) => {
          return a.name > b.name ? 1 : -1;
        })
      : Folder.file.sort((a, b) => {
          return a.name > b.name ? -1 : 1;
        });
  } else if (t === "Size") {
    fileheader.size = !fileheader.size;
    fileheader.size
      ? Folder.file.sort((a, b) => {
          return a.size - b.size;
        })
      : Folder.file.sort((a, b) => {
          return b.size - a.size;
        });
  } else if (t === "Last") {
    fileheader.date = !fileheader.date;
    fileheader.date
      ? Folder.file.sort((a, b) => {
          return a.mtime - b.mtime;
        })
      : Folder.file.sort((a, b) => {
          return b.mtime - a.mtime;
        });
  }
  gendom(file, Folder);
});
quick.addEventListener("click", () => {
  if (file.path === "/") {
    if (file.classList.contains("edit")) {
      file.classList.remove("edit");
    } else {
      file.classList.add("edit");
    }
  } else {
    if (quicklists.indexOf(file.path) === -1) quicklists.push(file.path);
    localStorage.quicklists = JSON.stringify(quicklists);
    pushTip("Added quickLink", file.path);
  }
});
chatName.addEventListener("input", () => {
  CHAT.name = chatName.innerText;
});
window.addEventListener("focus", () => {
  CHAT.time && reconnect();
});
forchat.addEventListener("click", () => {
  curfile.innerHTML = "Chat";
  toggleType(chatHist);
  chatVal.focus();
  reconnect();
});
$("#showoprt").addEventListener("click", () => {
  filectn.classList.contains("oprt") ? (filectn.classList.remove("oprt"), mobile && filectn.classList.remove("nothree")) : (filectn.classList.add("oprt"), mobile && filectn.classList.add("nothree"));
});
function reconnect() {
  if (wschat.readyState !== 1) {
    wschat = new WebSocket("ws://" + location.host + "/:chat");
    wschat.onmessage = (e) => {
      if (e.data.search(/(\d+\.){3}\d+:\d+/) === 0) {
        CHAT.ip = e.data;
      } else {
        try {
          let d = JSON.parse(e.data);
          if (d.message) {
            pushTip(d.message);
            return;
          }
          let c = nE("div", 0, "chat", `<div class="user"><a>${d.name}</a><span>${d.ip}</span></div><div class="content">${d.chat}</div>`);
          CHAT.time = d.time;
          d.ip === CHAT.ip && (c.className += " You");
          chatHist.append(c);
          chat.scrollTop = chatHist.offsetHeight;
        } catch (e) {
          pushTip(e);
        }
      }
    };
    wschat.onclose = () => {
      pushTip("Chat disconnected");
    };
    wschat.onopen = () => {
      pushTip("Chat connected");
      wschat.send(JSON.stringify({ time: CHAT.time }));
    };
    wschat.onerror = () => {
      pushTip("Chat Error");
    };
  }
}
$("#save").addEventListener("click", () => {
  Post(current.path, pre.innerText.replaceAll('\n\n','\n'));
});
pre.style.whiteSpace = "nowrap";
$("#wrap").addEventListener("click", () => {
  pre.style.whiteSpace = pre.style.whiteSpace === "nowrap" ? "normal" : "nowrap";
});
$("#send>button").addEventListener("click", () => {
  wschat.send(JSON.stringify({ name: CHAT.name, chat: chatVal.value }));
  chatVal.value = "";
});
chatVal.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") {
    wschat.send(JSON.stringify({ name: CHAT.name, chat: chatVal.value }));
    chatVal.value = "";
  }
});
var uploads = $("input#uploads");
function gendom(cur, dir = { folder: [], file: [], dir: "" }, hst = 0) {
  Folder = dir;
  let ni = 0;
  curpath.innerHTML = dir.dir;
  if (hst) {
    if (dir.dir !== hstryStack[hstryStack[0]]) {
      hstryStack[0] += 1;
      while (hstryStack.length > hstryStack[0]) hstryStack.pop();
      hstryStack.push(dir.dir);
    }
  }
  if (current) current.classList.remove("current");
  current = null;
  prevPath = cur.path;
  let tok = '?token='+Tok;
  if (((cur.innerHTML = ""), (cur.path = "/" + dir.dir), "/" !== cur.path[cur.path.length - 1] && (cur.path += "/"), dir.dir)) {
    let f = nE("div", 0, "folder flex", "<div>..</div><div></div><div></div>");
    (f.path = cur.path.slice(0, cur.path.lastIndexOf("/", cur.path.length - 2) + 1)), "/" === f.path && (f.path = "/*"), (f.folder = !0), (f.name = ".."), cur.append(f);
  }
  dir.folder.forEach((i) => {
    let f = nE("div", 0, "folder flex", `<div>${i.name}</div><div></div><div>${i.mts}</div>`);
    (f.path = cur.path + i.name + "/"), (f.folder = !0), (f.name = i.name), (f.ind = ni), ni++, cur.append(f);
  }),
    (ni = 0),
    dir.file.forEach((i) => {
      let ext = "unk",
        d = i.name.lastIndexOf(".");
      d > 0 && i.name.length - d < 6 && (ext = i.name.slice(d + 1).toLowerCase());
      let f = nE("div", 0, "flex file " + ext);
      (f.path = cur.path + i.name), (f.file = ext), (f.type = i.type), (f.name = i.name), cur.append(f);
      f.uri = encURL(f.path)+tok;
      f.innerHTML = `<div>${i.name}</div><div>${getSize(i.size)}</div><div>${i.mts}</div><div class="oprt"><div class="but rename"></div><div class="but delete"></div><a href="${f.uri}" download="${f.name}" class="but download"></a></div`;
      f.ind = ni;
      ni++;
    }),
    (localStorage.lastPath = cur.path === "/" ? "/*" : cur.path);
  if (dir.dir === "") {
    quicklists.forEach((v) => {
      let f = nE("div", 0, "link flex", `<div>${v}</div><div></div><div class="remove">❌</div>`);
      (f.path = v), (f.folder = !0), (f.draggable = !0), (f.name = v), cur.append(f);
    });
  }
}
function getSize(n) {
  let s = 0;
  for (; n > 1024; ) (n /= 1024), s++;
  return n.toFixed(3 - n.toFixed().length) + UNIT[s];
}
function toggleShow(n) {
  n ? (last === video && last.pause(), ((filectn.className = last.parentElement.className = ""), Ehide(astext)), show.classList.remove("show")) : show.classList.contains("show") || (mobile || (filectn.className = "collapse nothree"), show.classList.add("show"));
}
function toggleType(newEle, uri,path = null) {
  toggleShow(), last === video && last.pause(), path && ((newEle.src = uri), (curfile.innerHTML = `<a href="${newEle.src}">${path}</a>`), newEle === video && (video.firstElementChild.src = uri)), (last.parentElement.className = ""), (newEle.parentElement.className = "show"), (last = newEle);
  (newEle === audio || newEle === video) && newEle.play();
}
var fadeOutTip = (t, n = 3000) => {
  setTimeout(() => {
    (t.className += " fade"),
      (tips.style.paddingTop = t.offsetHeight + 11 + "px"),
      setTimeout(() => {
        (tips.style.paddingTop = 0), t.remove();
      }, 250);
  }, n);
};
function pushTip(title, content = "", auto = true) {
  let t = nE("div", 0, "tip", `<div class="title">${title}</div><div class="content">${content}</div>`);
  tips.append(t), auto && fadeOutTip(t);
  return t;
}
function refresh() {
  Get(localStorage.lastPath, (r) => {
    (r = JSON.parse(r)), gendom(file, r);
  }),
    mobile && toggleShow(1);
}
// image next/previous
image.prt = image.parentElement;
image.prt.addEventListener("touchstart", (e) => {
  if (e.touches.length > 1) image.xy = 0;
  else {
    image.xy = 1;
    let t = e.touches[0];
    image.sx = t.screenX;
    image.sy = t.screenY;
  }
});
image.prt.addEventListener("touchend", (e) => {
  if (image.xy) {
    let t = e.changedTouches[0];
    image.sx -= t.screenX;
    image.sy -= t.screenY;
    if (Math.abs(image.sy) < 100 && Math.abs(image.sx) > 20) {
      let i = 0;
      if (image.sx > 0) {
        toggleFile(1);
      } else {
        toggleFile(1, 1);
      }
    }
  }
});
// image wheel
image.scale = 1;
image.ox = 0;
image.oy = 0;
image.addEventListener("wheel", (e) => {
  image.scale += e.wheelDelta / 500;
  image.scale <= 0.2 && (image.scale = 0.2);
  image.style.transform = `scale(${image.scale})`;
  // console.log(e.offsetX,e.offsetY);
  // console.log(img.offsetX)
  image.ox = e.offsetX;
  image.oy = e.offsetY;
  image.style.transformOrigin = `${image.ox}px ${image.oy}px`;
  e.preventDefault();
  return false;
});
resize(image, image, "left", "top");
musiclist.addEventListener("mouseenter", () => {
  musiclist.classList.add("show");
  clearTimeout(musiclist.tmo);
});
musiclist.addEventListener("mouseleave", () => {
  clearTimeout(musiclist.tmo);
  musiclist.tmo = setTimeout(() => {
    musiclist.classList.remove("show");
  }, 2e3);
});
$("#formusiclist").addEventListener("click", () => {
  musiclist.classList.toggle("show");
});
uploads.addEventListener("input", () => {
  for (let i = 0; i < uploads.files.length; i++) {
    Post(localStorage.lastPath + uploads.files[i].name, uploads.files[i]);
    refresh();
  }
}),
  $("#refresh").addEventListener("click", refresh),
  $("#forterminal").addEventListener("click", () => {
    curfile.innerHTML = "Terminal";
    toggleType(stdout), stdin.focus();
  }),
  stdout.addEventListener("click", () => {
    stdin.focus();
  }),
  stdin.addEventListener("keydown", (e) => {
    "Enter" === e.key &&
      stdin.value &&
      ((stdout.innerText += stdin.value + "\n"),
      runCmd(
        stdin.value,
        (r) => {
          (stdout.innerText += r), (terminal.scrollTop = stdout.offsetHeight), (stdin.value = "");
        },
        (ret = !0)
      ));
  }),
  (window.onresize = () => {
    window.innerWidth < 600 ? ((mobile = !0), show.classList.add("mobile"), (dcsty.prev = dcsty.getPropertyValue("--left")), dcsty.setProperty("--left", "0%")) : ((mobile = !1), show.classList.remove("mobile"), dcsty.setProperty("--left", "30%"));
  });
window.addEventListener("beforeprint", () => {
  docu.className = "print";
});
window.addEventListener("afterprint", () => {
  docu.className = "";
});
window.addEventListener("popstate", (e) => {
  toggleShow(1);
  // <!-- parseInt(getComputedStyle(show).left)!==window.innerWidth && (get) 返回上一级 -->
  window.history.pushState(null, null, "#");
  if (wschat.readyState === 1) {
    e.preventDefault();
    return false;
  }
});
window.onbeforeunload = (e) => {
  toggleShow(1);
  window.history.pushState(null, null, "#");
  if (wschat.readyState === 1) {
    e.preventDefault();
    return false;
  }
};
window.history.pushState(null, null, "#");
function toggleFile(sameType = true, prev = false) {
  if (current) {
    let i = current.ind;
    if (!sameType) {
      if (prev) {
        i--;
      } else {
        i++;
      }
    } else if (!prev) {
      for (i++; i < Folder.file.length; i++) {
        if (Folder.file[i].type === current.type) {
          break;
        }
      }
    } else {
      for (i--; i >= 0; i--) {
        if (Folder.file[i].type === current.type) {
          break;
        }
      }
    }
    if (i < 0) {
      pushTip("Reached top");
    } else if (i >= Folder.file.length) {
      pushTip("Reached end");
    } else {
      i++;
      openFile(file.children[Folder.folder.length + i]);
    }
  }
}
astext.addEventListener("click", () => {
  openFile(current, true);
});
const Entity = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  ' ': '&nbsp;',
}
function toEt(s){
  return s.replace(/[&<>" ]/gm,(t)=>{return Entity[t]});
}
function openFile(ele, text) {
  let newe;
  current && current.classList.remove("current");
  current = ele;
  current.classList.add("current");
  toggleShow(),
    text
      ? ((newe = pre),
      Get(ele.path, (r) => {
        pre.innerHTML ='<p>'+ toEt(r).replaceAll('\n','</p><p>')+'</p>';
      }))
      : "html" === ele.file || "pdf" === ele.file || "htm" === ele.file
      ? (newe = ifr)
      : "text" === ele.type
      ? ((newe = pre),
      Get(ele.path, (r) => {
        pre.innerHTML ='<p>'+ toEt(r).replaceAll('\n','</p><p>')+'</p>';
      }))
      : "video" === ele.type || "ts" === ele.file
      ? ((newe = video), (track.src = ele.path.replace(/.\w{2,4}$/, ".srt")))
      : "audio" === ele.type || "flac" === ele.file
      ? (newe = audio)
      : "image" === ele.type || "png" === ele.file
      ? ((newe = image), (image.title = ele.name), (image.ind = ele.ind), (image.style.cssText = "transform:scale(1);transform-origin:50% 50%"), (image.left = image.top = 0))
      : "doc" === ele.file || "docx" === ele.file
      ? ((newe = doc),
        fetch(ele.path)
          .then((response) => response.arrayBuffer())
          .then((res) => {
            docx.renderAsync(res, doc, null, { ignoreWidth: true, ignoreHeight: true });
          }))
      : "xls" === ele.file || "xlsx" === ele.file || "csv" === ele.file
      ? ((newe = excel),
        (extName = ele.file),
        (ext = "." + extName),
        fetch(ele.path)
          .then((response) => response.arrayBuffer())
          .then((res) => {
            loadSheet(res, ext);
          }))
      : ((newe = link), (link.href = ele.uri), (link.innerHTML = ele.name)),
    Folder.file[ele.ind].size < 2097152 ? Eshow(astext) : Ehide(astext),
    toggleType(newe, ele.uri,ele.path);
}
document.addEventListener("keydown", (e) => {
  let i = 0;
  if (e.ctrlKey) {
    if (e.key === "ArrowUp") {
      if (e.altKey) {
        toggleFile(0, 1);
      } else {
        toggleFile(1, 1);
      }
      i = 1;
    } else if (e.key === "ArrowDown") {
      if (e.altKey) {
        toggleFile(0);
      } else {
        toggleFile(1);
      }
      i = 1;
    }
    if (i) {
      e.preventDefault();
      return false;
    }
  }
});
function Eshow(e) {
  e.style.display = "block";
}
function Ehide(e) {
  e.style.display = "none";
}
function Post(path, dat, callback) {
  // 先发不带数据的预检请求，否则上传完了结果无权创建文件就emo了，也可以认为是先创建文件，服务器不会检查是否存在，直接覆盖，有需要可js检查Folder.file
  let pxhr = new XMLHttpRequest();
  pxhr.open("POST", path);
  pxhr.setRequestHeader("Content-Type", "application/octet-stream");
  pxhr.onload = () => {
    if (pxhr.status === 200) {
      let xhr = new XMLHttpRequest();
      let prg, pg;
      xhr.open("POST", path),
        // xhr.setRequestHeader("token", PWD),
        xhr.setRequestHeader("Content-Type", "application/octet-stream"),
        (xhr.onload = () => {
          if (xhr.status === 200) {
            prg.firstElementChild.innerHTML = "Post file successfully";
            callback && callback(xhr.response);
          } else {
            prg.firstElementChild.innerHTML = "Error!";
          }
          fadeOutTip(prg);
        }),
        (xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            pg.update(e.loaded / e.total);
          }
        }),
        (xhr.onerror = () => {
          fadeOutTip(prg);
          pushTip("Failed to post file", path + "<br>" + xhr.responseText);
        }),
        xhr.send(dat);
      prg = pushTip("Uploading", path, 0);
      pg = Progress(prg);
    } else {
      pushTip("Error!", pxhr.response);
    }
  };
  pxhr.onerror = () => {
    pushTip("Error!", pxhr.response);
  };
  pxhr.send();
}
var Progress = (div) => {
  let c = nE("div", 0, "progress"),
    b = nE("div"),
    p = nE("p", 0, 0, "0%");
  c.append(b), c.append(p);
  div.append(c);
  c.update = (n) => {
    b.style.left = (n - 1) * 100 + "%";
    p.innerText = (n * 100).toFixed(0) + "%";
  };
  return c;
};
function resize(obj, tgt, x, y, g, rev = 1, mint = 0, call) {
  // x,y 只能是'left' top width height 属性
  let ix = x ? "offset" + x[0].toUpperCase() + x.slice(1) : "",
    iy = y ? "offset" + y[0].toUpperCase() + y.slice(1) : "";
  obj.onmousedown = function (e) {
    tgt.classList.add("notrst");
    e = e || window.event;
    var x_down = e.clientX;
    var y_down = e.clientY;
    var iix = parseInt(tgt[x]);
    var iiy = parseInt(tgt[y]);
    var ig = dcsty.getPropertyValue(g);
    var int = 0;
    function move(e) {
      //鼠标移动事件
      if (int < mint) {
        int++;
        return false;
      }
      e = e || window.event;
      var nx = e.clientX;
      var ny = e.clientY;
      var dx = nx - x_down;
      var dy = ny - y_down;
      iix !== undefined && (tgt.style[x] = tgt[x] = dx = iix + dx * rev + "px");
      iiy !== undefined && (tgt.style[y] = tgt[y] = dy = iiy + dy * rev + "px");
      g && dcsty.setProperty(g, nx + "px");
      call && call(x, y, dx, dy);
      e.preventDefault();
      int = 0;
      return false;
    }
    function mup(e) {
      move(e);
      tgt.classList.remove("notrst");
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", mup);
    }
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", mup);
    e.stopPropagation();
    return false; //阻止默认事件
  };
}
var lastX = 0;
resize(resizer, resizer, 0, 0, "--left", 1, 2, (x) => {
  if (lastX <= 700 && x > 700) {
    filectn.classList.remove("nothree");
  } else if (lastX > 700 && x <= 700) {
    filectn.classList.add("nothree");
  }
  lastX = x;
});

/*
 * 解析歌词字符串
 * [00:02.000] 编曲 : 肥肥安/周琦
 * 返回一个数组，结构是[{time:'43:01',words:'123'}]
 */
// 本来可以用浏览器自带的字幕track标签，但就是没用
function parseLyc(str) {
  var listarr = str.split("\n");
  listarr[0].indexOf("[img]") === 0 && (($("#music").style.backgroundImage = `url(${listarr[0].slice(5)})`), listarr.shift());
  var lryArr = [];
  str = '<p ind="0"></p>';
  let j = 1,
    obj = { time: 0, words: "" };
  lryArr.push(obj);
  let timestr = "";
  let wordstr = "";
  for (let i = 0; i < listarr.length; i++) {
    if (listarr[i].indexOf("]") > -1) {
      [timestr, wordstr] = listarr[i].split("]");
      if (timestr.search(/\[\d+:/) < 0) continue;
      str += `<p ind="${j}">${wordstr}</p>`;
      j++;
      obj = {
        time: parseTime(timestr),
        words: wordstr,
      };
      lryArr.push(obj);
    }
  }
  if (lryArr.length < 3) {
    str = "";
    for (let i = 0; i < listarr.length; i++) {
      str += `<p>${listarr[i]}</p>`;
    }
    lrc.innerHTML = str;
    return null;
  }
  lryArr.push({ time: obj.time + 8, words: "" });
  lrc.innerHTML = str + `<p ind="${j}"></p>`;
  return lryArr;
}
function parseTime(time) {
  let newstr = time.substr(1);
  let [min, second] = newstr.split(":");
  return +min * 60 + +second;
}
var lycData;
function findIndex() {
  lrc.children[audio.index] && (lrc.children[audio.index].className = "");
  var currentTime = audio.currentTime;
  if (!lycData) return;
  for (let i = 0; i < lycData.length; i++) {
    if (currentTime < lycData[i].time) {
      audio.index = i - 1;
      break;
    }
  }
  lrc.children[audio.index].className = "active";
  setOffset(1);
}
function setOffset(b) {
  if (b) {
    let c = lrc.children[audio.index];
    c.className = "active";
    c.innerHTML && scroll(lrc, lrc.scrollTop, c.offsetTop - lrc.offsetHeight / 2 + 28);
  }
  if (!lycData) return;
  if (audio.index + 1 < lycData.length && audio.currentTime > lycData[audio.index + 1].time) {
    lrc.children[audio.index].className = "";
    audio.index++;
    setOffset(1);
  }
}
lrc.addEventListener("click", (e) => {
  if (e.target.tagName === "P") {
    let i = e.target.getAttribute("ind");
    audio.currentTime = lycData[i].time;
    audio.play();
    lycData && findIndex();
  }
});

audio.index = 0;
// 播放时只要看下一行歌词是否到来，暂停后的播放（包括seek）则重新查找ind
audio.addEventListener("timeupdate", () => {
  lycData && (setOffset(), setTimeout(setOffset, 125));
});
audio.addEventListener("play", () => {
  lycData && setTimeout(findIndex, 80);
});
audio.onseeked = audio.play;
audio.addEventListener("loadedmetadata", () => {
  let dot = audio.src.lastIndexOf(".");
  $("#musichead").innerHTML = current.name;
  lycData = null;
  lrc.innerHTML = "";
  audio.lrcs = null;
  getLrcs();
});
function getLrcs(q = "") {
  runCmd({ oprt: "lrc", path: q ? q : current.path.slice(1) }, (r) => {
    if (r.indexOf("\n[") > 0) {
      lycData = parseLyc(r);
      findIndex();
    } else {
      r = JSON.parse(r);
      audio.lrcs = r;
      lrcs.innerHTML = "";
      for (let i = 0; i < r.length; i++) {
        let el = nE("div", 0, "lyrics", `<img src="${r[i].img}"><div><p>${r[i].name} - ${r[i].artist}</p><p> ${r[i].duration}  ${r[i].album}</p></div>`);
        el.ind = i;
        if (!lycData && r[i].lrc) {
          r[i].lrc = "[img]" + r[i].img + "\n" + r[i].lrc;
          lycData = parseLyc(r[i].lrc);
          findIndex();
          el.classList.add("active");
          lrcs.last = el;
          audio.lrcind = i;
          $("#music").style.backgroundImage = `url(${r[i].img})`;
        }
        lrcs.append(el);
      }
    }
  });
}
$("#savelrc").addEventListener("click", () => {
  if (audio.lrcs) {
    let lc = audio.lrcs[audio.lrcind];
    let p = audio.src.slice(0, audio.src.lastIndexOf(".")) + ".lrc";
    Post(p, lc.lrc);
  } else {
    getLrcs(current.path.slice(current.path.lastIndexOf("/"), current.path.lastIndexOf(".")));
  }
});
var searchlrc = $("#searchlrc");
searchlrc.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    getLrcs(searchlrc.value);
  }
});
lrcs.addEventListener("click", (e) => {
  let el = e.target;
  while (!el.className) {
    el = el.parentElement;
  }
  lrcs.last && lrcs.last.classList.remove("active");
  lrcs.last = lrcs.children[el.ind];
  lrcs.last.classList.add("active");
  audio.lrcind = el.ind;
  let lc = audio.lrcs[el.ind];
  if (lc.lrc) {
    lc.lrc.indexOf("[img]") < 0 && (lc.lrc = "[img]" + lc.img + "\n" + lc.lrc);
    lycData = parseLyc(lc.lrc);
    findIndex();
  } else {
    runCmd({ oprt: "lrc", url: lc.url }, (r) => {
      lc.lrc = "[img]" + lc.img + "\n" + r;
      lycData = parseLyc(lc.lrc);
      findIndex();
    });
  }
});
var Scroll = [0.008, 0.03, 0.067, 0.117, 0.179, 0.25, 0.329, 0.413, 0.5, 0.587, 0.671, 0.75, 0.821, 0.883, 0.933, 0.97, 0.992, 1];
function scroll(el, start, end, i = 0) {
  if (start === end) {
    return;
  }
  i === 0 && (el.det = end - start);
  let tar = start + el.det * Scroll[i];
  el.scrollTo(0, tar);
  i++;
  if (i < Scroll.length) {
    requestAnimationFrame(() => {
      scroll(el, start, end, i);
    });
  }
}

musiclist.show = !mobile;
mobile && (musiclist.className = "");
var Rem = $("#Remote");
var rmtIMG = $("#Remote>img");
var Remote = {};
/**
 *
 * @param {String} s
 * @param {Number} l
 * @returns String
 */
function getKey(s, l) {
  if (s.length === 1) {
    return s;
  } else {
    if (s === "Control") {
      s = "ctrl";
    } else if (s === "Escape") {
      s = "esc";
    } else if (s === "CapsLock") {
      s = "caps_lock";
    } else if (s.indexOf("Arrow") === 0) {
      s = s.slice(5);
    } else if (s.indexOf("Page") === 0) {
      s = "page_" + s.slice(4);
    }
    s = s.toLowerCase();
    if (s === "ctrl" || s === "alt" || s === "shift") {
      if (l === 1) {
        s += "_l";
      } else if (l === 2) {
        s += "_r";
      }
    }
    console.log(s);
    return s;
  }
}
var forkey = $("#forkey"),
  keyboard = $("div.keyboard"),
  fps = $("#fps");
forkey.key = 0;
forkey.addEventListener("click", (e) => {
  forkey.key = !forkey.key;
  keyboard.style.bottom = forkey.key ? "0" : "-100%";
});
fps.time = 200;
fps.addEventListener("click", (e) => {
  let t = e.target;
  if (t.tagName === "LI") {
    fps.time = 1000 / t.innerText;
    fps.lastElementChild.style.display = "none";
    fps.firstElementChild.innerText = t.innerText;
    Pause();
    Pause();
  } else {
    fps.lastElementChild.style.display = "block";
  }
});
function getXY(e) {
  return [e.pageX - rmtIMG.offsetLeft, e.pageY - rmtIMG.offsetTop];
}
var hasMove = 0;
var mouseDown = [];
function Pause() {
  toggleType(rmtIMG);
  if (Remote.readyState !== 1) {
    freshWH();
    addEvent();
    Remote = new WebSocket("ws://" + location.host + "/:remote");
    console.log(rmtIMG.offsetHeight, rmtIMG.offsetWidth);
    Remote.sendCmd = (d) => {
      d.control = 1;
      if (d.xy) {
        d.xy[0] = parseInt((d.xy[0] / rmtIMG.offsetWidth) * WH[0]);
        d.xy[1] = parseInt((d.xy[1] / rmtIMG.offsetHeight) * WH[1]);
      }
      d = JSON.stringify(d);
      Remote.send(d);
    };
    Remote.onmessage = (e) => {
      rmtIMG.src = URL.createObjectURL(new Blob([e.data], { type: "application/octet-stream" }));
      URL.revokeObjectURL(Remote.url);
      Remote.url = rmtIMG.src;
    };
    Remote.int = setInterval(() => {
      Remote.send(JSON.stringify({ frame: 1 }));
    }, fps.time);
    Remote.onopen = () => {
      Remote.send(JSON.stringify({ frame: 1 }));
    };
  } else {
    Remote.pause = !Remote.pause;
    if (Remote.pause) {
      clearInterval(Remote.int);
      pushTip("Paused");
      document.removeEventListener("keydown", keydown);
      document.removeEventListener("keyup", keyup);
      rmtIMG.removeEventListener("mousemove", mousemove);
      rmtIMG.removeEventListener("mousedown", mousedown);
      rmtIMG.removeEventListener("mouseup", mouseup);
      rmtIMG.removeEventListener("wheel", wheel);
      Rem.removeEventListener("contextmenu", contextmenu);
    } else {
      pushTip("Continue");
      Rem.requestFullscreen();
      Remote.int = setInterval(() => {
        Remote.send(JSON.stringify({ frame: 1 }));
      }, fps.time);
      addEvent();
    }
  }
}
let mousemove = (e) => {
    hasMove = 1;
    if (mouseDown) {
      Remote.sendCmd({ type: "mousedown", xy: mouseDown });
      mouseDown = 0;
    }
    Remote.sendCmd({ type: "move", xy: [e.offsetX, e.offsetY] });
  },
  mousedown = (e) => {
    hasMove = 0;
    mouseDown = [e.offsetX, e.offsetY];
  },
  mouseup = (e) => {
    Remote.sendCmd({ type: hasMove ? "mouseup" : "click", xy: [e.offsetX, e.offsetY] });
    hasMove = 0;
    mouseDown = 0;
  },
  wheel = (e) => {
    Remote.sendCmd({ type: "wheel", dxy: [-e.deltaX / 50, -e.deltaY / 50], xy: [e.offsetX, e.offsetY] });
  },
  contextmenu = (e) => {
    Remote.sendCmd({ type: "context", xy: [e.offsetX, e.offsetY] });
    e.preventDefault();
    return false;
  },
  // 单指点击，滚动；双指点击，右击
  touchmoved = 0,
  touch0 = 0,
  longmenu = 0,
  touch = 0,
  lastClick = {},
  touchstart = (e) => {
    touch = e.touches[0];
    if (e.touches.length === 1) {
      touch0 = touch;
      touch0.x3 = touch.clientX;
      touch0.time = new Date().getTime();
      setTimeout(() => {
        if (!touchmoved && touch0) {
          touch0.time = 0;
          longmenu = 1;
        }
      }, 500);
      }
  },
  touchmove = (e) => {
    if(longmenu){
      longmenu = 0;
      Remote.sendCmd({ type: "mousedown", xy: getXY(touch0) });
    }
    if (e.touches.length === 1) {
      let t = e.touches[0];
      if (touch0.time === 0) {
        touch0.time = 0;
        Remote.sendCmd({ type: "move", xy: getXY(t) });
      } else {
        let dxy = [(touch.clientX - t.clientX)/8, (t.clientY - touch.clientY)/5];
        touch = t;
        Remote.sendCmd({ type: "wheel", dxy: dxy, xy: getXY(touch0) });
      }
    }
    else if(e.touches.length===3){ 
      let t = e.touches[0];
      let d = t.clientX-touch0.x3;
      if(!touch0.three){touch0.three=1;
      Remote.sendCmd({type:'keydown',key:'alt'})}
      if(d>20){
        touch0.x3 = t.clientX;
        Remote.sendCmd({type:"tap",key:'tab'});
      }else if(d<-20){
        touch0.x3 = t.clientX;
        Remote.sendCmd({type:'keydown',key:'shift'});
        Remote.sendCmd({type:'tap',key:'tab'});
        Remote.sendCmd({type:'keyup',key:'shift'});
      }
    }
    touchmoved = 1;
  },
  touchend = (e) => {
    if (e.touches.length === 0) {
      if (!touchmoved) {
        if(longmenu){
          Remote.sendCmd({ type: "context", xy: getXY(touch0) });
          longmenu = 0;
        }
        else{
        let c = { xy: getXY(touch0), time: new Date().getTime() };
        if (c.time - lastClick.time < 1500 && Math.abs(c.xy[0] - lastClick.xy[0]) < 12 && Math.abs(c.xy[1] - lastClick.xy[1]) < 12) {
          c.xy = lastClick.xy;
        }
        Remote.sendCmd({ type: "click", xy: [c.xy[0], c.xy[1]] });
        lastClick = c;}
      } else if (touch0.time === 0) {
        Remote.sendCmd({ type: "mouseup", xy: getXY(e.changedTouches[0]) });
      }
      touch0 = 0;
    } else if (e.touches.length === 1 && !touchmoved) {
      Remote.sendCmd({ type: "context", xy: getXY(touch0) });
      touchmoved = 1;
    }
    if(touch0.three){
      Remote.sendCmd({type:'keyup',key:'alt'});
      Remote.sendCmd({type:'keyup',key:'shift'});
      touch0.three=0;
    }
    touchmoved = 0;
  };
let keydown = (e) => {
  let b = e.ctrlKey || e.shiftKey || e.altKey;
  let k = getKey(e.key, e.location);
  b && (k = k.toLowerCase());
  Remote.sendCmd({ type: "keydown", key: k });
  e.preventDefault();
  return false;
};
let keyup = (e) => {
  let b = e.ctrlKey || e.shiftKey || e.altKey;
  let k = getKey(e.key, e.location);
  b && (k = k.toLowerCase());
  Remote.sendCmd({ type: "keyup", key: k });
  e.preventDefault();
  return false;
};
function addEvent() {
  if (Mobile) {
    rmtIMG.addEventListener("touchstart", touchstart);
    rmtIMG.addEventListener("touchmove", touchmove);
    rmtIMG.addEventListener("touchend", touchend);
  } else {
    rmtIMG.addEventListener("mousemove", mousemove);
    rmtIMG.addEventListener("mousedown", mousedown);
    rmtIMG.addEventListener("mouseup", mouseup);
    rmtIMG.addEventListener("wheel", wheel);
    Rem.addEventListener("contextmenu", contextmenu);
  }
  document.addEventListener("keydown", keydown);
  document.addEventListener("keyup", keyup);
}
!Mobile &&
  keyboard.addEventListener("click", (e) => {
    let t = e.target;
    if (t.tagName === "LI") {
      let k = t.className || t.innerText[0].toLowerCase();
      Remote.sendCmd({ type: "keydown", key: k });
      Remote.sendCmd({ type: "keyup", key: k });
    }
  });
keyboard.addEventListener("touchstart", (e) => {
  let t = e.changedTouches[0].target;
  if (t.tagName === "LI") {
    let k = t.className || t.innerText[0].toLowerCase();
    Remote.sendCmd({ type: "keydown", key: k });
  }
});
keyboard.addEventListener("touchend", (e) => {
  let t = e.changedTouches[0].target;
  if (t.tagName === "LI") {
    let k = t.className || t.innerText[0].toLowerCase();
    Remote.sendCmd({ type: "keyup", key: k });
  }
});
keyboard.addEventListener("contextmenu", (e) => {
  e.preventDefault();
  return false;
});
remote.addEventListener("click", Pause);

function freshWH(){
  Get(':getWH',(r)=>{
    let wh = r.split(',');
    if(wh.length===2){
      WH = wh;
    }else{
      console.log("error GET Resolution WH, Response:",r);
    }
  })
}