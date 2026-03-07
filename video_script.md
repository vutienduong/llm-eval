# Video Script: Gioi thieu LLM Eval Framework (10-15 phut)

## 1) Muc tieu video

- Gioi thieu bai toan: AI agent tra loi hay nhung kho do do tin cay.
- Trinh bay cach app nay danh gia reliability theo test case incident.
- Demo chay that va doc ket qua dashboard.
- Ket thuc bang roadmap va call-to-action.

## 2) Doi tuong nguoi xem

- AI engineer, backend engineer, SRE, PM ky thuat.
- Da biet co ban ve LLM/agent, can framework de danh gia chat luong.

## 3) Tong thoi luong de xuat

- Tong: 12 phut (co the dao dong 10-15 phut).

## 4) Timeline chi tiet + loi thoai mau

### 0:00 - 0:45 | Hook

Noi:
"Ban co mot AI agent tra loi rat tu tin, nhung moi lan production gap su co thi ket qua lai khong on dinh. Video nay minh se cho ban mot framework nho gon de do duoc do tin cay cua agent: do accuracy, hallucination rate, tool correctness, latency, va cost."

Hinh anh:
- Cat nhanh 2-3 man hinh: log incident, output agent, dashboard score.

### 0:45 - 2:00 | Bai toan va huong giai quyet

Noi:
"Van de lon nhat khong phai agent tra loi sai 100%, ma la sai khong du doan duoc. Vi vay, minh can bo test co cau truc va metric ro rang. App nay dung file YAML test case, chay agent, cho judge cham diem, tong hop thanh report."

Hinh anh:
- Mo `prd.md`, highlight architecture.
- Chuyen sang `README.md` section Architecture.

### 2:00 - 3:30 | Kien truc va giao tiep component

Noi:
"Flow chay rat thang: test_cases -> runner -> output -> judge -> metrics -> dashboard. Diem can chu y la contract giao tiep voi agent subprocess: framework gui payload JSON vao stdin va nhan JSON qua stdout."

Hinh anh:
- Scroll 2 so do Mermaid trong README.
- Zoom vao phan contract `response`, `tool_calls`, `cost_usd`.

### 3:30 - 5:00 | Walkthrough code nhanh

Noi:
"`run_eval.py` la orchestrator. `agent_runner.py` co 2 che do: demo va subprocess. `judge_model.py` cham theo tieu chi ky vong + tool call + hallucination heuristic + latency. Sau do `metrics.py` aggregate va `reporting.py` xuat JSON, Markdown, HTML."

Hinh anh:
- Lan luot mo:
  - `run_eval.py`
  - `agent_runner.py`
  - `judge_model.py`
  - `reporting.py`

### 5:00 - 7:30 | Demo chay thuc te

Noi:
"Bay gio minh chay demo runner de thay pipeline end-to-end."

Terminal commands de quay:

```bash
source .venv/bin/activate
llm-eval --cases test_cases.yaml --output-dir reports/video-demo
```

Noi tiep:
"Lenh da evaluate 3 case va tao 3 artifact: report.json, report.md, dashboard.html."

Hinh anh:
- Hien output command.
- Mo `reports/video-demo/dashboard.html`.

### 7:30 - 9:30 | Doc ket qua dashboard

Noi:
"O day minh xem nhanh Overall score, Accuracy, Hallucination, Tool correctness va latency. O bang Case Results, minh thay case nao cham thap de debug prompt hoac tool-use logic."

Hinh anh:
- Scroll dashboard:
  - Hero KPI cards
  - Category scores
  - Case results
  - Integration readiness (LangSmith/DeepEval/TruLens)

### 9:30 - 11:00 | Cai nay dung trong team nhu the nao

Noi:
"Trong team, ban co the dung framework nay nhu quality gate: moi lan doi prompt hoac doi model, chay bo test nay truoc khi release. Neu score roi xuong nguong, dung merge."

Hinh anh:
- Mo `test_cases.yaml` va giai thich cach them case moi.
- Minh hoa 1 case "CPU spike".

### 11:00 - 12:00 | Roadmap va ket

Noi:
"Ban roadmap tiep theo gom: multi-model benchmark, LLM judge backend, trace voi LangSmith, feedback voi TruLens, va CI fail threshold. Neu ban muon, minh co the lam tiep phan so sanh nhieu model trong 1 lan chay."

Hinh anh:
- Mo section "Next roadmap" trong README.
- Outro with repo tree.

## 5) Shot list (quay nhanh)

- Shot A: talking head 20-30 giay de mo bai.
- Shot B: screen record README architecture.
- Shot C: code walkthrough split-screen.
- Shot D: terminal run command.
- Shot E: dashboard deep dive.
- Shot F: closing CTA.

## 6) CTA de xuat

- "Comment model ban muon benchmark."
- "Neu can, minh se lam phan 2: ket noi agent that qua subprocess + CI gating."

## 7) Ghi chu san xuat

- Keep pace nhanh, 1 y chinh moi 30-45 giay.
- Moi khi doi section, hien lower-third title.
- Khi demo terminal, zoom font lon de de doc.
- Uu tien 1080p, 30fps, audio sach.
