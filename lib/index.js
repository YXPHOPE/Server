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
  searchlrc = $("#searchlrc"),
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
  curpath = $("#curpath"),
  remote = $("#remote"),
  menu = $("#menu"),
  drop = $("#drop"),
  lrc = $("#lrc"),
  lrcs = $("#lrcs>div"),
  uploads = $("input#uploads"),
  Rem = $("#Remote"),
  rmtIMG = $("#Remote>img"),
  forkey = $("#forkey"),
  keyboard = $("div.keyboard"),
  fps = $("#fps"),
  tlcm = $("#communicate"),
  reqpwd = $("div#reqpwd"),
  board = $("#board"),
  docu = document.documentElement,
  dcsty = document.documentElement.style,
  Prog = {},
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
  Scroll = [0.008, 0.03, 0.067, 0.117, 0.179, 0.25, 0.329, 0.413, 0.5, 0.587, 0.671, 0.75, 0.821, 0.883, 0.933, 0.97, 0.992, 1],
  encURL = (s) => {
    return encodeURIComponent(s).replace("%3A", ":").replace(/%2F/g,'/');
  },
  current = null,
  WH = [1920, 1080],
  History = new Hist(),
  CHAT = { time: 0, ip: "", name: "蒙面大侠" };
const CS = {
  65539: "default",
  0: "none",
  65563: "help",
  65567: "pointer",
  65561: "progress",
  65543: "wait",
  49743883: "cell",
  65545: "crosshair",
  65541: "text",
  303762077: "vertical-text",
  29429383: "alias",
  31919477: "copy",
  65557: "move",
  65559: "no-drop",
  14093987: "grab",
  41092819: "grabbing",
  65553: "e-resize",
  65555: "n-resize",
  65551: "ne-resize",
  65549: "nw-resize",
  9241657: "col-resize",
  41684679: "row-resize",
  52956727: "zoom-in",
  90771627: "zoom-out",
};
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
    if (this.getItem(sKey) === null) {
      pushTip("Cookie Error", "Your browser dose not support cookie or you disable the cookie.");
      return false;
    }
    return true;
    P;
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
window.innerWidth <= 600 && ((mobile = !0), show.classList.add("mobile"), dcsty.setProperty("--left", "0%")), (last = video), (file.path = "");
dcsty.prev = dcsty.getPropertyValue("--left");
let lastPath = location.href.replace(/^.*(\?|\&)path=([^\&]*)(\&.*|$)/,'$2');
(lastPath===location.href)&& (lastPath = localStorage.lastPath || "/*",
  prevPath = "/*");
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
    200 === xhr.status ? callback && callback(xhr.response) : 403 === xhr.status && (Eshow(reqpwd), reqpwd.io.focus());
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
  filename.indexOf("\\") >= 0 && (filename = filename.replace(/\\/g, "/"));
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
        History.new(ele.path);
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
      History.new("/*");
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
  Post(current.path, pre.innerText.replace(/\n\n/g, "\n"));
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
function gendom(cur, dir = { folder: [], file: [], dir: "" }) {
  Folder = dir;
  let ni = 0;
  curpath.innerHTML = dir.dir;
  if (current) current.classList.remove("current");
  current = null;
  prevPath = cur.path;
  let tok = "?token=" + Tok;
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
      f.uri = encURL(f.path) + tok;
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
  let l = 3 - n.toFixed().length;
  l < 0 && (l = 0);
  return n.toFixed(l) + UNIT[s];
}
function toggleShow(n) {
  n ? (last === video && last.pause(), ((filectn.className = last.parentElement.className = ""), Ehide(astext)), show.classList.remove("show")) : show.classList.contains("show") || (mobile || (filectn.className = "collapse nothree"), show.classList.add("show"));
}
function toggleType(newEle, uri, path = null) {
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
reqpwd.io = reqpwd.querySelector("input");
reqpwd.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    reqpwd.check();
  }
});
reqpwd.addEventListener("click", (e) => {
  e = e.target;
  if (e.id === "2no") {
    reqpwd.io.value = "";
    Ehide(reqpwd);
  } else if (e.id === "2yes") {
    reqpwd.check();
  }
});
reqpwd.check = () => {
  let p = reqpwd.io.value;
  if (p === "") return;
  let l = p.split("");
  for (let i = 0; i < l.length; ++i) {
    l[i] = String.fromCharCode(p.charCodeAt(i) ^ 0x66);
  }
  p = l.join("");
  runCmd({ oprt: "token", pwd: p }, (r) => {
    r = JSON.parse(r);
    if (r.token) {
      Tok = r.token;
      Cookies.setItem("token", r.token, 1800) ? pushTip("Success") : pushTip("Failed");
      Ehide(reqpwd);
      reqpwd.io.value = "";
      PWD = p;
      refresh();
    } else {
      pushTip("Error", r);
    }
  });
};
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
  (window.onresize = OnResize);
function OnResize() {
  window.innerWidth < 600 ? ((mobile = !0), show.classList.add("mobile"), (dcsty.prev = dcsty.getPropertyValue("--left")), dcsty.setProperty("--left", "0%")) : ((mobile = !1), show.classList.remove("mobile"), dcsty.setProperty("--left", "30%"));
}
OnResize();
window.addEventListener("beforeprint", () => {
  docu.className = "print";
});
window.addEventListener("afterprint", () => {
  docu.className = "";
});
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
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  " ": "&nbsp;",
};
function toEt(s) {
  return s.replace(/[&<>" ]/gm, (t) => {
    return Entity[t];
  });
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
          pre.innerHTML = "<p>" + toEt(r).replace(/\n/g, "</p><p>") + "</p>";
        }))
      : "html" === ele.file || "pdf" === ele.file || "htm" === ele.file
      ? (newe = ifr)
      : "text" === ele.type
      ? ((newe = pre),
        Get(ele.path, (r) => {
          pre.innerHTML = "<p>" + toEt(r).replace(/\n/g, "</p><p>") + "</p>";
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
    toggleType(newe, ele.uri, ele.path);
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
  } else if (e.key === "F5") {
    window.location = "/index.html";
    e.preventDefault();
    return false;
  }
});
function Eshow(e) {
  e.style.display = "block";
}
function Ehide(e) {
  e.style.display = "none";
}
function PostFrom(path, start, data, t) {
  let u = 0;
  t = t || 0;
  let xhr = new XMLHttpRequest();
  xhr.open("POST", path),
    // xhr.setRequestHeader("token", PWD),
    xhr.setRequestHeader("Content-Type", "application/octet-stream"),
    xhr.setRequestHeader("Start", start),
    (xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        Prog[path][0] += e.loaded - u;
        u = e.loaded;
      }
    }),
    (xhr.onerror = () => {
      if (t < 2) {
        PostFrom(path, start, data, t);
        t++;
      }
      pushTip("Error to post file " + start, path + "<br>" + xhr.responseText);
    }),
    xhr.send(data);
}
function Post(path, dat, callback) {
  // 先发不带数据的预检请求，否则上传完了结果无权创建文件就emo了，也可以认为是先创建文件，服务器不会检查是否存在，直接覆盖，有需要可js检查Folder.file
  let pxhr = new XMLHttpRequest();
  pxhr.open("POST", path);
  pxhr.setRequestHeader("Content-Type", "application/octet-stream");
  pxhr.setRequestHeader("Size", dat.size || 1);
  pxhr.onload = () => {
    if (pxhr.status === 200) {
      let xhr = new XMLHttpRequest();
      let prg, pg;
      // 使用8线程传输
      prg = pushTip("Uploading", path, 0);
      pg = Progress(prg);
      pg.update(0);
      if (typeof dat === "string") {
        let Xhr = new XMLHttpRequest();
        Xhr.open("POST", path);
        Xhr.setRequestHeader("Content-Type", "plain/text");
        Xhr.onload = () => {
          if (Xhr.status === 200) {
            prg.firstElementChild.innerHTML = "Post file successfully";
            callback && callback(xhr.response);
            pg.update(1);
          } else {
            prg.firstElementChild.innerHTML = xhr.responseText;
          }
          setTimeout(() => {
            PostFrom(path, -1);
            fadeOutTip(prg);
          }, 2000);
        };
        Xhr.send(dat);
      } else {
        Prog[path] = [0, dat.size];
        let s;
        let e = dat.size;
        let per = parseInt(e / 8) + 1;
        for (let i = 0; i < 8; i++) {
          PostFrom(path, i * per, dat.slice(i * per, i * per + per));
        }
        let t = setInterval(() => {
          (s = Prog[path][0]), (e = Prog[path][1]);
          if (e === -1) {
            prg.firstElementChild.innerHTML = "Error!";
          } else if (s === e) {
            prg.firstElementChild.innerHTML = "Post file successfully";
            callback && callback(xhr.response);
          } else {
            pg.update(s / e);
            return;
          }
          pg.update(s / e);
          // 不能立即传输完毕请求，反正就是关闭文件必须晚于最后一个片段写入成功之后进行
          // 一切的文件上传后打不开大概率是这里的问题
          setTimeout(() => {
            PostFrom(path, -1);
            fadeOutTip(prg);
          }, 2000);
          clearInterval(t);
          // Prog中path对象不知道怎么删除，无妨，除非你一下给我传爆了
        }, 100);
      }
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
    tgt.className += "notrst resizing";
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
      tgt.classList.remove("resizing");
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
        time: parseTime(timestr)-0.08,
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
class SRT{
  vd = video;
  div = $('#srt');
  href = '';
  srt = [];
  crt = 0;
  aval = false;
  constructor(){
    this.vd = video.tagName==='VIDEO'?video: $('video');
    this.vd.addEventListener('loadedmetadata',()=>{
      this.loadSRT();
    })
    this.vd.addEventListener('seeked', ()=>{
      this.aval && this.process(this.vd.currentTime);
    });
    this.vd.addEventListener('timeupdate', ()=>{
      this.aval && this.process(this.vd.currentTime,this.crt)
    });
  }
  loadSRT(){
    // 使用默认的video标签，直接全屏会导致全屏元素以外的任何其他元素不可见 - 待改善
    let src = this.vd.src;
    let i = src.lastIndexOf('.');
    this.href = src.substring(0,i)+'.srt';
    this.aval = !1;
    this.div.style.top = 'calc(50% + '+(this.vd.offsetHeight/2-60)+'px)';
    Get(this.href,(r)=>{
      this.parseSrt(r);
      this.aval = this.srt.length>2;
      if(this.aval){
        this.div.innerHTML = '';
      }
    });
  }
  process(t,cur=-1){
    if(cur===-1){
      // 二分法寻找seek到的时间点t下的字幕
      let i=0,j=this.srt.length;
      let n=j>>1;
      while(j-i>1){
        this.srt[n].e>t?(j=n):(i=n);
        n = i+(j-i>>1); // 位移优先级低于加减乘除
      }
      // 最后j-i=1，n==i
      this.srt[i].e<t && this.srt[j].s<t && n++;
      this.crt = n;
      this.div.innerHTML = this.srt[n].c;
    }else if(cur<this.srt.length-1){
      // 万事万物只要分好所有情况就不会出错 哈哈
      if(this.srt[cur+1].e<=t || this.srt[cur].s>t){
        // 超过当前字幕的结束时间，或早于开始时间，都是异常情况，需要重新seek
        this.process(t);
      }
      // 此时已限定在 |[cur] gap [cur+1]| 这个时间段
      else if(this.srt[cur+1].s<=t){
        this.crt++;
        this.div.innerHTML = this.srt[this.crt].c;
      }
      else if(this.srt[cur].e<=t) {
        this.div.innerHTML = '';
      }
    }
  }
  parseSrt(s){
    s = s.split(/\r?\n/);
    let i = 0, j=0, l = s.length;
    this.srt = [{s:0,e:0.2,c:''}];
    for(;i<l;++i){
      if(s[i].search(/^\d+$/)!==-1){
        ++j;
        this.srt.push({s:0,e:0,c:''});
      }else if (s[i].indexOf('-->')>0){
        let t = s[i].split(/ *--> */)
        this.srt[j].s = parseTime(t[0])-0.09;
        this.srt[j].e = parseTime(t[1]);
      }else if(s[i]!==''){
        this.srt[j].c+=s[i]+'</br>';
      }
    }
    let e = this.srt[this.srt.length-1].e;
    this.srt.push({s:e+0.1,e:e+0.2,c:''});
  }
}
var Srt = new SRT();
function parseTime(s) {
  s[0]==='[' && (s = s.substring(1));
  s = s.replace(',','.').split(":");
  let l = s.length-1;
  return +s[l]+s[l-1]*60+(l===2?s[0]*3600:0);
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
    clearInterval(Remote.int);
    Remote.int = setInterval(() => {
      Remote.send(JSON.stringify({ frame: 1 }));
    }, fps.time);
  } else {
    fps.lastElementChild.style.display = "block";
  }
});
function getXY(e) {
  return [e.pageX - rmtIMG.offsetLeft, e.pageY - rmtIMG.offsetTop];
}
var hasMove = 0;
var mouseDown = [];
function RemClose(t, c) {
  pushTip(t, c);
  clearInterval(Remote.int);
  document.removeEventListener("keydown", keydown);
  document.removeEventListener("keyup", keyup);
  rmtIMG.removeEventListener("mousemove", mousemove);
  rmtIMG.removeEventListener("mousedown", mousedown);
  rmtIMG.removeEventListener("mouseup", mouseup);
  rmtIMG.removeEventListener("wheel", wheel);
  Rem.removeEventListener("contextmenu", contextmenu);
}
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
      if (typeof e.data === "string" && e.data.length < 16) {
        rmtIMG.style.cursor = CS[parseInt(e.data)];
      } else {
        rmtIMG.src = URL.createObjectURL(new Blob([e.data], { type: "application/octet-stream" }));
        URL.revokeObjectURL(Remote.securl);
        Remote.securl = Remote.url;
        Remote.url = rmtIMG.src;
      }
    };
    Remote.int = setInterval(() => {
      Remote.send(JSON.stringify({ frame: 1 }));
    }, fps.time);
    Remote.onopen = () => {
      Remote.send(JSON.stringify({ frame: 1 }));
    };
    Remote.onerror = (e) => {
      RemClose("Remote Websocket Error", "Please check if you have inputed password and your network connection.");
    };
    Remote.onclose = () => {
      RemClose("Remote Websocket closed", "");
    };
  } else {
    Remote.pause = !Remote.pause;
    if (Remote.pause) {
      RemClose("Remote Websocket paused", "");
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
    if (mouseDown && mouseDown[0] !== null) {
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
    if (longmenu) {
      longmenu = 0;
      Remote.sendCmd({ type: "mousedown", xy: getXY(touch0) });
    }
    if (e.touches.length === 1) {
      let t = e.touches[0];
      if (touch0.time === 0) {
        touch0.time = 0;
        Remote.sendCmd({ type: "move", xy: getXY(t) });
      } else {
        let dxy = [(touch.clientX - t.clientX) / 8, (t.clientY - touch.clientY) / 5];
        touch = t;
        Remote.sendCmd({ type: "wheel", dxy: dxy, xy: getXY(touch0) });
      }
    } else if (e.touches.length === 3) {
      let t = e.touches[0];
      let d = t.clientX - touch0.x3;
      if (!touch0.three) {
        touch0.three = 1;
        Remote.sendCmd({ type: "keydown", key: "alt" });
      }
      if (d > 20) {
        touch0.x3 = t.clientX;
        Remote.sendCmd({ type: "tap", key: "tab" });
      } else if (d < -20) {
        touch0.x3 = t.clientX;
        Remote.sendCmd({ type: "keydown", key: "shift" });
        Remote.sendCmd({ type: "tap", key: "tab" });
        Remote.sendCmd({ type: "keyup", key: "shift" });
      }
    }
    touchmoved = 1;
  },
  touchend = (e) => {
    if (e.touches.length === 0) {
      if (!touchmoved) {
        if (longmenu) {
          Remote.sendCmd({ type: "context", xy: getXY(touch0) });
          longmenu = 0;
        } else {
          let c = { xy: getXY(touch0), time: new Date().getTime() };
          if (c.time - lastClick.time < 1500 && Math.abs(c.xy[0] - lastClick.xy[0]) < 12 && Math.abs(c.xy[1] - lastClick.xy[1]) < 12) {
            c.xy = lastClick.xy;
          }
          Remote.sendCmd({ type: "click", xy: [c.xy[0], c.xy[1]] });
          lastClick = c;
        }
      } else if (touch0.time === 0) {
        Remote.sendCmd({ type: "mouseup", xy: getXY(e.changedTouches[0]) });
      }
      touch0 = 0;
    } else if (e.touches.length === 1 && !touchmoved) {
      Remote.sendCmd({ type: "context", xy: getXY(touch0) });
      touchmoved = 1;
    }
    if (touch0.three) {
      Remote.sendCmd({ type: "keyup", key: "alt" });
      Remote.sendCmd({ type: "keyup", key: "shift" });
      touch0.three = 0;
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

function freshWH() {
  Get(":getWH", (r) => {
    let wh = r.split(",");
    if (wh.length === 2) {
      WH = wh;
    } else {
      console.log("error GET Resolution WH, Response:", r);
    }
  });
}

tlcm.addEventListener("click", () => {
  if (!tlcm.active) {
    tlcm.active = 1;
    const constraints = { audio: true };
    tlcm.audio = nE("audio");
    tlcm.ws = new WebSocket("ws://" + location.host + "/:tlcm");
    tlcm.ws.onopen = () => {
      tlcm.ws.send(1);
      tlcm.ms = new MediaSource();
      tlcm.audio.src = URL.createObjectURL(tlcm.ms);
      tlcm.ms.addEventListener("sourceopen", (e) => {
        tlcm.sb = tlcm.ms.addSourceBuffer("audio/mpeg");
        tlcm.sb.addEventListener("updateend", () => {
          tlcm.ms.endOfStream();
          tlcm.audio.play();
        });
      });
      navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
          const options = {
            audioBitsPerSecond: 64000,
            mimeType: "video/webm;codecs=vp8,opus",
          };
          tlcm.MR = new MediaRecorder(stream, options);
          tlcm.MR.ondataavailable = (e) => {
            tlcm.ws.send(e.data);
          };
          tlcm.MR.start();
        })
        .catch((error) => {
          pushTip("Error on recorder", error.message);
        });
    };
    tlcm.ws.onmessage = (e) => {
      tlcm.sb.appendBuffer(e.data);
    };
    tlcm.ws.onclose = () => {
      tlcm.MR.stop();
    };
  } else {
    tlcm.active = 0;
    tlcm.ws.close();
  }
});

window.onunload = (e) => {
  history.pushState(null, "", "/index.html");
  e.preventDefault();
  return false;
};
window.onbeforeunload = (e) => {
  toggleShow(1);
  history.pushState(null, "", "/index.html");
  if (wschat.readyState === 1) {
    e.preventDefault();
    return false;
  }
};
// 函数式构建类
function Hist() {
  this.stack = new Array();
  this.lmt = 20;
  this.cur = -1;
  history.pushState({n:-1},null,'/index.html');
  this.forward = () => {
    if (this.cur < this.stack.length - 1) {
      Get(this.stack[++this.cur], (r) => {
        (r = JSON.parse(r)), gendom(file, r, 1);
      });
    }
  };
  this.back = () => {
    if (this.cur > 0) {
      Get(this.stack[--this.cur], (r) => {
        (r = JSON.parse(r)), gendom(file, r, 1);
      });
    }
  };
  this.new = (p) => {
    let i = this.stack.length - this.cur - 1;
    while (i > 0) {
      this.stack.pop();
      i--;
    }
    this.stack.push(p);
    this.cur++;
    history.pushState({ n: this.cur }, "", '/index.html?path='+p);
  };

  window.addEventListener("popstate", (e) => {
    e.preventDefault();
    if (mobile && show.classList.contains("show")) {
      toggleShow(1);
      return '';
    }
    if (!e.state) return false;
    let n = e.state.n;
    if (n === this.cur - 1) {
      this.back();
    } else if (n === this.cur + 1) {
      this.forward();
    }
    return false;
  }, false);
}
$("#forboard").addEventListener("click", () => {
  if (board.show) {
    board.style.display = "none";
    board.show = 0;
  } else {
    board.style.display = "block";
    board.show = 1;
  }
});
board.ndpwd = board.querySelector("#ndpwd");
board.pwd = board.querySelector("#pwd");
board.pre = board.querySelector("#prepwd");
board.addEventListener("click", (e) => {
  let id = e.target.id;
  if (id === "pwdsave") {
    runCmd({ oprt: "setpwd", pre: board.pre.value, ndpwd: board.ndpwd.value === "on", pwd: board.pwd.value });
  } else if (id === "restart") {
    runCmd({ oprt: "restart" });
  }
});
