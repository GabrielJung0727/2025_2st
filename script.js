import { COURSES } from "./data/courses.js";

const courseListEl = document.querySelector("[data-course-list]");
const courseCodeEl = document.querySelector("[data-course-code]");
const courseNameEl = document.querySelector("[data-course-name]");
const courseSummaryEl = document.querySelector("[data-course-summary]");
const courseTagsEl = document.querySelector("[data-course-tags]");
const assignmentMenuEl = document.querySelector("[data-assignment-menu]");
const assignmentTitleEl = document.querySelector("[data-assignment-title]");
const assignmentDateEl = document.querySelector("[data-assignment-date]");
const assignmentSummaryEl = document.querySelector("[data-assignment-summary]");
const assignmentTagsEl = document.querySelector("[data-assignment-tags]");
const fileListEl = document.querySelector("[data-file-list]");
const emptyStateEl = document.querySelector("[data-empty-state]");
const runBlockEl = document.querySelector("[data-run-block]");
const runListEl = document.querySelector("[data-run-list]");
const previewBlockEl = document.querySelector("[data-preview-block]");
const previewLabelEl = document.querySelector("[data-preview-label]");
const previewOpenEl = document.querySelector("[data-preview-open]");
const previewIframeEl = document.querySelector("[data-preview-iframe]");
const previewCodeEl = document.querySelector("[data-preview-code]");
const searchInput = document.querySelector("[data-search]");
const courseCountEl = document.getElementById("course-count");
const assignmentCountEl = document.getElementById("assignment-count");

let currentCourseId = COURSES[0]?.id ?? null;
let currentAssignmentId = COURSES[0]?.assignments?.[0]?.id ?? null;
let searchTerm = "";
let currentPreview = null;

function hexToRgb(hex) {
  if (!hex || typeof hex !== "string") return null;
  const normalized = hex.replace("#", "");
  if (![3, 6].includes(normalized.length)) return null;
  const chunk = normalized.length === 3 ? normalized.split("").map((c) => c + c) : normalized.match(/.{1,2}/g);
  if (!chunk) return null;
  const [r, g, b] = chunk.map((c) => parseInt(c, 16));
  return { r, g, b };
}

function setAccent(accent) {
  const fallback = "#7ff0d5";
  const color = accent || fallback;
  const rgb = hexToRgb(color);
  document.documentElement.style.setProperty("--accent", color);
  if (rgb) {
    document.documentElement.style.setProperty("--accent-rgb", `${rgb.r}, ${rgb.g}, ${rgb.b}`);
  }
}

function updateCounts() {
  const totalAssignments = COURSES.reduce((sum, course) => sum + course.assignments.length, 0);
  courseCountEl.textContent = `${COURSES.length}개 과목`;
  assignmentCountEl.textContent = `${totalAssignments}개 과제`;
}

function getCurrentCourse() {
  return COURSES.find((course) => course.id === currentCourseId) ?? COURSES[0];
}

function renderCourseList() {
  courseListEl.innerHTML = "";
  COURSES.forEach((course) => {
    const card = document.createElement("button");
    card.className = `course-card ${course.id === currentCourseId ? "active" : ""}`;
    card.type = "button";
    card.innerHTML = `
      <div class="course-title">
        <span class="pill" style="border-color: rgba(var(--accent-rgb), 0.3); color: var(--text); background: rgba(var(--accent-rgb), 0.08);">${course.code}</span>
        ${course.name}
      </div>
      <p class="muted">${course.summary}</p>
      <div class="pill">과제 ${course.assignments.length}개</div>
    `;
    card.addEventListener("click", () => setCourse(course.id));
    courseListEl.appendChild(card);
  });
}

function renderCourseHeader(course) {
  courseCodeEl.textContent = `과목 ${course.code}`;
  courseNameEl.textContent = course.name;
  courseSummaryEl.textContent = course.summary;
  courseTagsEl.innerHTML = "";
  course.tags?.forEach((tag) => {
    const span = document.createElement("span");
    span.className = "tag";
    span.textContent = tag;
    courseTagsEl.appendChild(span);
  });
}

function filteredAssignments(course) {
  if (!searchTerm) return [...course.assignments];
  const lower = searchTerm.toLowerCase();
  return course.assignments.filter((assignment) => {
    const inTitle = assignment.title.toLowerCase().includes(lower);
    const inSummary = assignment.summary?.toLowerCase().includes(lower);
    const inTags = assignment.tags?.some((tag) => tag.toLowerCase().includes(lower));
    return inTitle || inSummary || inTags;
  });
}

function renderAssignmentMenu(course) {
  const assignments = filteredAssignments(course);
  assignmentMenuEl.innerHTML = "";

  if (!assignments.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = searchTerm ? "검색 결과가 없습니다." : "아직 등록된 과제가 없습니다.";
    assignmentMenuEl.appendChild(empty);
    renderAssignmentDetail(null);
    return;
  }

  if (!assignments.find((item) => item.id === currentAssignmentId)) {
    currentAssignmentId = assignments[0]?.id ?? null;
  }

  assignments.forEach((assignment) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = `menu-item ${assignment.id === currentAssignmentId ? "active" : ""}`;
    item.dataset.assignmentId = assignment.id;
    item.innerHTML = `
      <strong>${assignment.title}</strong>
      <small>${assignment.summary}</small>
    `;
    item.addEventListener("click", () => {
      currentAssignmentId = assignment.id;
      renderAssignmentMenu(course);
      renderAssignmentDetail(assignment);
    });
    assignmentMenuEl.appendChild(item);
  });

  const current = assignments.find((a) => a.id === currentAssignmentId);
  renderAssignmentDetail(current);
}

function renderFiles(files = []) {
  fileListEl.innerHTML = "";
  if (!files.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "첨부된 파일이 없습니다.";
    fileListEl.appendChild(empty);
    return;
  }

  files.forEach((file) => {
    const anchor = document.createElement("a");
    anchor.className = "file-card";
    anchor.href = encodeURI(file.path);
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";

    const label = document.createElement("span");
    label.className = "file-label";
    label.textContent = file.label;

    const path = document.createElement("span");
    path.className = "file-path";
    path.textContent = file.path;

    anchor.appendChild(label);
    anchor.appendChild(path);
    fileListEl.appendChild(anchor);
  });
}

function getPreviewType(path) {
  const ext = path.split(".").pop()?.toLowerCase() || "";
  if (["html", "htm", "pdf"].includes(ext)) return "iframe";
  if (["py", "js", "ts", "tsx", "css", "md", "txt", "json", "csv", "yaml", "yml", "ipynb"].includes(ext)) {
    return "code";
  }
  return null;
}

async function setPreview(preview) {
  if (!preview) {
    previewBlockEl.hidden = true;
    currentPreview = null;
    return;
  }

  const type = getPreviewType(preview.path);
  currentPreview = { preview, type };

  if (!type) {
    previewBlockEl.hidden = true;
    return;
  }

  previewBlockEl.hidden = false;
  previewLabelEl.textContent = preview.label || preview.path;
  previewOpenEl.hidden = false;
  previewOpenEl.href = encodeURI(preview.path);

  previewIframeEl.hidden = true;
  previewCodeEl.hidden = true;

  if (type === "iframe") {
    previewIframeEl.src = encodeURI(preview.path);
    previewIframeEl.hidden = false;
  } else if (type === "code") {
    previewCodeEl.textContent = "로딩 중...";
    previewCodeEl.hidden = false;
    try {
      const res = await fetch(encodeURI(preview.path));
      if (!res.ok) throw new Error(res.statusText);
      const text = await res.text();
      previewCodeEl.textContent = text;
    } catch (err) {
      previewCodeEl.textContent = `미리보기 로드 실패: ${err}`;
    }
  }
}

function renderRun(run = []) {
  if (!run.length) {
    runBlockEl.hidden = true;
    runListEl.innerHTML = "";
    return;
  }

  runBlockEl.hidden = false;
  runListEl.innerHTML = "";

  run.forEach((item) => {
    const card = document.createElement("div");
    card.className = "run-card";

    const title = document.createElement("div");
    title.className = "run-label";
    title.textContent = item.label || "실행";
    card.appendChild(title);

    (item.commands || []).forEach((cmd) => {
      const row = document.createElement("div");
      row.className = "cmd-row";

      const code = document.createElement("code");
      code.textContent = cmd;

      const button = document.createElement("button");
      button.type = "button";
      button.className = "copy-btn";
      button.textContent = "복사";
      button.dataset.copy = cmd;

      row.appendChild(code);
      row.appendChild(button);
      card.appendChild(row);
    });

    runListEl.appendChild(card);
  });
}

function renderAssignmentDetail(assignment) {
  if (!assignment) {
    assignmentTitleEl.textContent = "과제를 선택하세요";
    assignmentDateEl.textContent = "";
    assignmentSummaryEl.textContent = "왼쪽 메뉴에서 과제를 선택하면 요약과 파일이 표시됩니다.";
    assignmentTagsEl.innerHTML = "";
    fileListEl.innerHTML = "";
    previewBlockEl.hidden = true;
    renderRun([]);
    emptyStateEl.hidden = false;
    return;
  }

  emptyStateEl.hidden = true;
  assignmentTitleEl.textContent = assignment.title;
  assignmentDateEl.textContent = assignment.date || "";
  assignmentSummaryEl.textContent = assignment.summary ?? "";
  assignmentTagsEl.innerHTML = "";
  assignment.tags?.forEach((tag) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = tag;
    assignmentTagsEl.appendChild(chip);
  });

  renderRun(assignment.run || []);
  renderFiles(assignment.files || []);
  setPreview(assignment.preview);
}

function setCourse(courseId) {
  currentCourseId = courseId;
  const course = getCurrentCourse();
  setAccent(course.accent);
  currentAssignmentId = course.assignments?.[0]?.id ?? null;
  searchTerm = "";
  if (searchInput) searchInput.value = "";
  renderCourseList();
  renderCourseHeader(course);
  renderAssignmentMenu(course);
}

function init() {
  updateCounts();
  setAccent(getCurrentCourse()?.accent);
  renderCourseList();
  renderCourseHeader(getCurrentCourse());
  renderAssignmentMenu(getCurrentCourse());

  if (searchInput) {
    searchInput.addEventListener("input", (event) => {
      searchTerm = event.target.value.trim();
      renderAssignmentMenu(getCurrentCourse());
    });
  }

  runListEl.addEventListener("click", async (event) => {
    const target = event.target;
    if (target instanceof HTMLButtonElement && target.dataset.copy) {
      try {
        await navigator.clipboard.writeText(target.dataset.copy);
        const original = target.textContent;
        target.textContent = "완료";
        setTimeout(() => {
          target.textContent = original;
        }, 900);
      } catch (err) {
        console.error(err);
      }
    }
  });
}

init();
