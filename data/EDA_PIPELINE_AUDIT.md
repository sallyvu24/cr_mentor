# Audit solution so với kiến thức và pipeline EDA của khóa học (4 file `Python_EDA_Day_1-4.ipynb`)

> **Cập nhật 05/11/2026:** các đề xuất ở đây đã được thẩm định lại trên dữ liệu và P1–P3 đã được áp dụng vào notebook chính. Có đính chính cho C2, C5 và cách chữa của P3: xem `EDA_IMPROVEMENT_VERIFICATION.md`. Số mục của notebook nêu dưới đây là số mục của bản trước khi sửa.

**Đối tượng audit:** `notebooks/sydney_student_rent_eda` (notebook chính, gọi tắt **MAIN**, số mục theo notebook) và `notebooks/00_data_extraction_overview` (gọi tắt **OVERVIEW**), cùng `scripts/01-06`.
**Quy ước nguồn:** **[R]** đọc từ code/output đã lưu trong repo; **[V]** tôi tự tính lại, script ở `data/verification/` (`v6_pipeline_audit.py` cho audit này).

---

## 0. Tóm tắt điều hành

| Câu hỏi | Trả lời |
|---|---|
| Đã áp dụng kiến thức bài giảng chưa? | **Có, ở mức rộng và sâu.** Trong 28 kỹ thuật tôi rút ra từ Day 2-4: **9 vượt kỳ vọng, 12 đạt, 6 chỉ làm một phần, 1 chưa làm**. 27/28 (96%) có mặt; 21/28 (75%) đạt hoặc vượt. |
| Đã áp dụng logic/pipeline EDA chưa? | **Có.** Pipeline 6 bước của Day 1 được thực hiện đủ, trong đó bước 1, 2, 5 vượt xa mức bài giảng; bước 3, 4, 6 đạt nhưng còn khoảng trống cụ thể. Dự án còn thể hiện đúng tính **lặp** của EDA (proposal v1 → v2 → bổ sung dữ liệu). |
| Điểm mạnh nhất so với bài giảng | Khung 5 câu hỏi xử lý lỗi dữ liệu của Day 3 ("có hợp lệ không? nguồn gốc? giữ lại thì sao? sửa được không? quyết định") được **vận dụng có lý giải** cho trùng lặp và giá trị bất thường; làm sạch được **đếm từng bước** và **đối chiếu chéo** pandas với SQL. |
| Khoảng trống chính | (1) Chưa phân tích **mẫu thiếu dữ liệu** (Day 2-3); (2) **bước co giãn (scaling) hình thức**: `zscore` không bao giờ được gọi, min-max không đổi kết quả nào; (3) **không điều tra** các dòng bị loại như outlier, và boxplot ẩn outlier; (4) khung 5 câu hỏi **không áp dụng cho dữ liệu thiếu**; (5) chưa kiểm tra **nhất quán giữa file 2018 và các năm sau**; (6) biểu đồ cho **phát hiện chính** và quy đổi **AUD/tuần** còn thiếu. |

---

## 1. Chuẩn đối chiếu: bốn file bài giảng dạy gì

| File | Nội dung cốt lõi (rút từ cell code/markdown) |
|---|---|
| **Day 1** | EDA là gì và lợi ích ("nhìn dữ liệu trước khi giả định; tìm lỗi rõ ràng; tìm mẫu; phát hiện outlier; tìm quan hệ"). **Quy trình EDA 6 bước:** (1) hiểu câu hỏi/giả thuyết; (2) hiểu nguồn dữ liệu (đã có gì, đủ chưa, cần thêm gì); (3) biến đổi dữ liệu cho sạch và dùng được; (4) trực quan hóa; (5) mô hình hóa bằng thống kê; (6) truyền đạt thông điệp hành động. Python nền tảng. |
| **Day 2** | Ca nghiên cứu e-commerce: *nêu câu hỏi kinh doanh và giới hạn phạm vi dữ liệu theo sự kiện thực tế* (bỏ dữ liệu ngoài khoảng thời gian). Rồi: nhập dữ liệu có tham số (`compression`, `nrows`, `index_col`); `head/tail`; thuộc tính (`shape`, `dtypes`, `columns`); `info/describe`; tách cột phân loại/số bằng list comprehension; **kiểm tra null** (`isnull().sum()`, tỷ lệ, **biểu đồ cột mức đầy đủ dữ liệu**, **`any/all(axis=1)` để tìm mẫu thiếu**); **trùng lặp** (cả dòng, theo tập cột khóa); đổi tên cột; **lọc** (mask, `isin`, `~`, `.str`, `query`, DuckDB SQL); **khoảng giá trị** (`hist`, `describe`); **điều tra outlier** (lọc đúng các dòng lạ rồi lần theo đơn hàng); biến phân loại (`unique`, `nunique`, `value_counts`); boxplot. Cùng điều khiển luồng (`if/for/while`, comprehension). |
| **Day 3** | **7 vấn đề chất lượng dữ liệu** (thiếu, trùng, không nhất quán, outlier, không liên quan, lỗi thời, "mù chữ dữ liệu") và **khung 5 câu hỏi** khi xử lý (hợp lệ không? nguồn lỗi ở đâu? giữ lại thì sao? sửa được không? quyết định). **Xử lý thiếu:** tìm mẫu (theo nhóm sản phẩm), **điền bằng trung vị của nhóm** (`fillna`). Boxplot (cả theo nhóm). **IQR** (kể cả vector hóa cho mọi cột số; ghi chú cận dưới âm là vô nghĩa). **Co giãn đặc trưng:** chuẩn hóa min-max, chuẩn hóa z-score, log. **Hàm và lambda** (bài tập: hàm chuẩn hóa nhận bảng và cột). |
| **Day 4** | `groupby` và `agg` (kể cả đặt tên cột kết quả), `sort_values`, `nunique`; **`merge`** (`how`, `on`, `left_on/right_on`, **`indicator=True` rồi `_merge.value_counts()` để kiểm tra dòng không khớp**); **chuỗi thời gian** (`to_datetime`, `.dt.year/month/day_name/dayofweek`, `lineplot`). |

---

## 2. PHẦN A. Kiến thức đã áp dụng, chỉ rõ section

**Thang mức:** **Vượt** = làm hơn mức bài giảng và có lý giải; **Đạt** = áp dụng đúng; **Một phần** = có nhưng thiếu bước cốt lõi; **Chưa** = không thấy.

| # | Kỹ thuật (bài giảng) | Nơi áp dụng trong solution | Mức | Nhận xét |
|---|---|---|---|---|
| **Day 2** | | | | |
| 1 | Nhập dữ liệu có tham số | MAIN §2.1 (`read_parquet(columns=…)`), §2.2 (`read_csv(dtype=str, encoding="utf-8-sig")`, `read_excel(header=5, usecols=…)`), §3.1 (`skiprows=3`); OVERVIEW §2-§9 phần *Extract* (API CKAN, file zip, shapefile) | **Vượt** | 62 file Excel gộp thành 1 bảng; tải tự động có thử lại |
| 2 | `head/tail` | MAIN §2.1 (`head`, `tail(3)`), §3.2 (`sample(5)`); OVERVIEW mục *Overview* của từng nguồn | Đạt | |
| 3 | `shape/dtypes/info/describe` | MAIN §2.1 (`info()`, `describe(percentiles=[.01,.05,.5,.95,.99])`), §2.2 hàm `profile()`; OVERVIEW §1 hàm `card()` | Đạt | `info()` chỉ dùng cho bảng bond; các nguồn khác dùng hàm tự viết tương đương |
| 4 | Tách cột phân loại/số và lập hồ sơ mọi cột | MAIN §2.1 (`value_counts` mã loại nhà); OVERVIEW `card()` (distinct, missing) | Một phần | Không có vòng lặp lập hồ sơ cho *tất cả* cột, chỉ vài cột chính |
| 5 | Kiểm tra null (`isna().sum()`, tỷ lệ) | MAIN §2.1 "Missing values, codes and ranges"; §2.2 `profile()`; OVERVIEW *Quality notes* | Đạt | thiếu tiền thuê 1.50%, thiếu số phòng 2.64% **[R]** |
| 6 | **Mẫu thiếu dữ liệu** (`any/all(axis=1)`, theo nhóm) và biểu đồ mức đầy đủ | không có | **Chưa** | Xem C1: mẫu thiếu **không ngẫu nhiên** |
| 7 | Trùng lặp (theo tập cột khóa) | MAIN §2.1 "Duplicates" (5 trường; tỷ trọng theo loại nhà), §2.2 `profile()` | **Vượt** | Đo 6.0% (112,664 dòng) rồi **giải thích vì sao giữ**; tôi kiểm tra: xóa trùng không đổi kết luận **[V]** |
| 8 | Đổi tên/làm sạch tên cột | MAIN §2.2 (`rename(columns=lambda c: …)`), §3.1 (`b18.columns=…`) | Đạt | |
| 9 | Lọc (mask, `isin`, `between`, `~`, `.str`) | MAIN §2.1, §2.2 (`.str.replace().str.strip().str.title()` chuẩn hóa nhãn sector), §3.1, §9.1 (`.str.contains`) | Đạt | |
| 10 | DuckDB SQL | MAIN §2.1 (đếm theo tháng), §3.1 (nhật ký làm sạch), §4.2 (trung vị bằng SQL đối chiếu pandas, có `assert`) | **Vượt** | Dùng SQL như công cụ *kiểm chứng chéo*, vượt mức "biết cú pháp" |
| 11 | Khoảng giá trị (`describe`, `hist`) | MAIN §2.1 (histogram cắt ở $3,000), §3.3 (histogram E2) | Đạt | |
| 12 | Phát hiện **và điều tra** outlier | MAIN §2.1 "Outliers: IQR fences versus hard limits" (bảng chéo IQR × giới hạn cứng) | Một phần | Phát hiện và lý giải tốt; **không lần theo các dòng bị loại** (Day 2 cell "lọc đúng dòng lạ"); xem C3 |
| 13 | Biến phân loại (`unique/value_counts`) | MAIN §2.1 (mã loại nhà, thứ trong tuần), §2.2 (sector) | Đạt | |
| 14 | Boxplot (cả theo nhóm) | MAIN §2.1 (theo loại nhà, thang log), §6.1 (theo nhóm exposure × cửa sổ) | Đạt | `showfliers=False` **ẩn đúng thứ boxplot dùng để phát hiện** (outlier) |
| **Day 3** | | | | |
| 15 | **7 vấn đề chất lượng dữ liệu** | MAIN §2.3 bảng tóm tắt; §2.1-§2.2 | **Vượt** | Đủ 7: thiếu, trùng, không nhất quán (mã lạ, nhãn sector), outlier, không liên quan (Central Coast, 861 khóa hết hạn), lỗi thời (DoE 1 năm, bản sao UAT 2018, Airbnb 1 thời điểm), "mù chữ dữ liệu" (đọc chú giải mã `U`) |
| 16 | **Khung 5 câu hỏi xử lý** | MAIN §2.1: trùng ("không có mã bond…nên không xóa") và outlier ("sẽ cắt chính thị trường cần nghiên cứu…") | Một phần | Áp dụng tốt cho 2 vấn đề; **không áp dụng cho dữ liệu thiếu** |
| 17 | Xử lý thiếu: tìm mẫu rồi điền/loại | MAIN §3.1 (loại, có đếm) | Một phần | Quyết định **loại** hợp lý nhưng không có bước "tìm mẫu" trước; `fillna` chỉ dùng điền 0 cho số đếm (§9.1, §9.2) |
| 18 | IQR | MAIN §2.1 hàm `iqr_bounds()` áp trên **log rent** | **Vượt** | Đúng tinh thần ghi chú Day 3 (cận dưới âm vô nghĩa → chuyển log); so sánh với giới hạn cứng: IQR gắn cờ 50,651 dòng so với 3,272 **[R]** |
| 19a | Co giãn min-max / z-score | MAIN §3.3 (`minmax`, `zscore`; áp cho 6 biến thể exposure) | Một phần | **Hình thức**: `zscore` không được gọi lần nào; min-max chỉ dùng cho heatmap Spearman, vốn bất biến với co giãn đơn điệu. Xem C6 |
| 19b | Biến đổi log | MAIN §2.1 (log rent), §4.4 (log trước khi tách xu hướng), §5.1 (`100·ln(B/A)`) | **Vượt** | Dùng log đúng chỗ để đo % thay đổi đối xứng; tránh được hack `log(0)` của bài giảng nhờ giới hạn $100 |
| 20 | Hàm và lambda | MAIN §1 `md`; §2.1 `iqr_bounds`; §2.2 `profile`; §3.3; §3.6 `bp_dates`; §5.1 `build_changes`; §6 `cluster_bootstrap`, `grade_evidence`; OVERVIEW §1 `fetch`, `card`, `check`, `register` | **Vượt** | Có docstring và kiểu dữ liệu. Hạn chế: quy tắc làm sạch chưa đóng gói thành hàm, và bị **viết hai lần** (xem P6) |
| **Day 4** | | | | |
| 21 | `groupby` và `agg` có đặt tên | MAIN §3.2, §3.5, §4.2, §5.3, §7, §9 (ví dụ `.agg(bonds=("rent","size"), …)`) | **Vượt** | Nhiều cấp nhóm (postcode × phân khúc × giai đoạn) |
| 22 | `sort_values`, `nunique` | MAIN §3.2, §5.3, §7 | Đạt | |
| 23 | `merge` (how, on, **validate**) | MAIN §2.2 (`validate="m:1"`), §4.2 (`validate="1:1"`); OVERVIEW §2-§9, §11 (đối chiếu DCJ với bond) | Đạt | Dùng `validate`, một bước *vượt* so với bài giảng |
| 24 | `merge` + **`indicator`** (kiểm dòng không khớp) | MAIN §2.2 in tỷ lệ khớp CRICOS (100%) cho **một** phép ghép; scripts `05`, `06` có ~10 phép `merge`, không `validate`/`indicator` | Một phần | **[V]** Hậu quả thực: 0 giá trị thiếu ở các cột khóa của bảng phân tích → chưa gây hại, nhưng thiếu cơ chế |
| 25 | `to_datetime` và `.dt` | MAIN §3.1 (`format="%d/%m/%Y", errors="coerce"`), §2.1 (`dt.day_name`), §4.1 (`dt.to_period("M")`); OVERVIEW *Extract*, *Coverage in time* | Đạt | |
| 26 | Thao tác chuỗi thời gian | MAIN §3.6 (`rolling(12)`, `resample("QS")`), §4.1 (chỉ số tháng, `rolling(3)`, **`reindex` ra lưới tháng đầy đủ để lộ khoảng trống 2019-2020**), §4.4 (tách xu hướng bằng trung bình trượt căn giữa, hồ sơ theo tháng lịch) | **Vượt** | Xa hơn bài giảng (chỉ `lineplot` trên số tổng hợp) |
| 27 | Trực quan chuỗi thời gian | MAIN §3.6, §4.1, §4.4 | Đạt | |

> **Đếm:** vì dòng 19 tách thành 19a/19b nên tổng là **28 kỹ thuật**. **Vượt 9** (1, 7, 10, 15, 18, 19b, 20, 21, 26); **Đạt 12** (2, 3, 5, 8, 9, 11, 13, 14, 22, 23, 25, 27); **Một phần 6** (4, 12, 16, 17, 19a, 24); **Chưa 1** (6).

---

## 3. PHẦN B. Pipeline EDA 6 bước (Day 1): đã vận dụng đến đâu

| Bước | Nội dung bài giảng | Bằng chứng trong solution | Mức | Khoảng trống |
|---|---|---|---|---|
| **1. Hiểu câu hỏi/giả thuyết** | Ca nghiên cứu Day 2: nêu câu hỏi kinh doanh, giới hạn phạm vi theo sự thật bối cảnh | MAIN đầu notebook: Project overview, End user and decision, 4 câu hỏi RQ1-RQ4, Scope; `PROJECT_BRIEF.md`; persona có tài liệu gốc | **Vượt** | Giả thuyết còn **ngầm**: chưa nêu rõ "dự đoán dấu gì, kết quả nào sẽ bác bỏ" (ví dụ nhà riêng cùng khu là bác bỏ nếu nhịp hồi cũng có) |
| **2. Hiểu nguồn dữ liệu** | Đã có gì? Đủ chưa? Cần thêm gì? | OVERVIEW toàn bộ (8 nguồn × *What it is → Extract → Overview → Data dictionary → Quality notes → Role*); `DATA_ENRICHMENT_ASSESSMENT.md`; `DATASET_DECISION.md` (nguồn nào *không* lấy, kèm thử nghiệm GTFS) | **Vượt** | MAIN **chưa hấp thụ** kết quả bước này (phần chờ 6 quyết định) |
| **3. Biến đổi dữ liệu** | Làm sạch, sẵn sàng phân tích | MAIN §2-§3: nhật ký làm sạch có số, SQL, `assert` panel = nhật ký, pandas = SQL | **Đạt (cao)** | 4 khoảng trống ở Phần C: mẫu thiếu, điều tra outlier, nhất quán 2018, scaling hình thức |
| **4. Trực quan hóa** | Histogram, boxplot, scatter... | MAIN: histogram/boxplot (§2.1), bản đồ choropleth (§3.4, §5.2), chỉ số theo thời gian (§4.1), mùa vụ (§4.4), heatmap (§3.3, §6.4), scatter (§6.2), cột hành lang (§5.3, §7) | **Đạt** | (i) thiếu **biểu đồ cho phát hiện chính** (đường "chênh lệch Cao − Thấp theo thời gian"); (ii) `showfliers=False`; (iii) thiếu biểu đồ mức đầy đủ dữ liệu (Day 2) |
| **5. Mô hình hóa thống kê** | "Xác định và giải thích quan hệ bằng thống kê" | MAIN §6: chênh lệch trung vị theo nhóm, **cluster bootstrap** theo SA3, Spearman, hoán vị, độ bền (60 đặc tả, bỏ từng hành lang), **quy tắc xếp hạng A/B/C đặt trước** | **Vượt** | Vượt xa phạm vi 4 file. Còn thiếu: placebo (nhà 3-4 phòng ngủ) dù dữ liệu đã tính; trung vị chưa hiệu chỉnh cơ cấu |
| **6. Thông điệp hành động** | "Nhìn về phía trước: sẽ làm gì với insight? giá trị gì?" | MAIN §10.2: khuyến nghị đổi theo hạng bằng chứng; §10.5 hướng phát triển; `PROJECT_BRIEF.md` cho business | **Đạt** | (i) kết quả chỉ ở **điểm phần trăm**, chưa quy ra **AUD/tuần** dù `PROPOSAL_v2.md` §4.5 hứa; (ii) chưa nối thẳng từng khuyến nghị với một quyết định của người dùng |

**Đánh giá chung về logic pipeline:** pipeline được vận dụng **đúng thứ tự và đúng tinh thần**; chất lượng cao nhất ở các bước dùng lập luận (1, 2, 5), thấp hơn ở các bước đòi hỏi *kiểm tra thủ tục theo khuôn bài giảng* (mẫu thiếu, điều tra outlier, `indicator`).

---

## 4. PHẦN C. Bằng chứng định lượng cho các khoảng trống **[V]** (`v6_pipeline_audit.py`)

**C1. Mẫu thiếu dữ liệu không ngẫu nhiên (kỹ thuật #6, #16, #17).**
- Cả hai trường cùng thiếu: 23,972 dòng; chỉ thiếu tiền thuê: 4,232; chỉ thiếu số phòng ngủ: 25,666.
- **Thiếu tập trung vào mã `U` ("không rõ")**: 37.3% thiếu tiền thuê và 49.9% thiếu số phòng ngủ; trong khi căn hộ `F` chỉ thiếu 0.28% và 0.87%.
- Thiếu **giảm dần theo năm**: tiền thuê 2.11% (2021) → 1.00% (2026).
- **Ý nghĩa:** quyết định *loại* là hợp lý, và còn an toàn hơn notebook nói, vì mã `U` rơi vào nhóm `other`, không nằm trong phân khúc phân tích (`f01`, `f2`). Nhưng lập luận này **chưa được viết ra**, và đó chính là bước "tìm mẫu rồi mới quyết định" của Day 2-3.

**C2. Mất dòng âm thầm khi đọc file 2018 (kỹ thuật #15, #25).** `coerce` + `dropna` làm mất **1 dòng** (ngày không đọc được; 331,880 → 331,879). Không đáng kể, nhưng nhật ký không in con số, trái với tuyên bố "mọi dòng bị loại đều được đếm".

**C3. Các dòng bị giới hạn cứng loại (kỹ thuật #12).** Dưới $100: 2,664 dòng (trung vị **$60**; 100 dòng bằng 0); trên $5,000: 708 dòng (trung vị **$6,332**). **48% số dòng bị loại thuộc loại nhà `O`** (ngoài phân khúc phân tích). Quy tắc lành tính, nhưng bằng chứng này không có trong notebook.

**C4. Nhất quán chéo trường (Day 3, vấn đề "không nhất quán").** Nhà `H` ghi 0 phòng ngủ: 1,724 dòng (0.12%); căn hộ `F` có ≥5 phòng ngủ: 579 dòng; 8,446 dòng (0.57%) lệch hơn 3 lần hoặc dưới 1/3 so với trung vị cùng postcode-phân khúc-năm. Nhỏ, chưa xử lý, nên liệt kê.

**C5. IQR theo nhóm (kỹ thuật #12, #14, #18; Day 3 boxplot theo nhóm).** Áp IQR *trong từng năm* cho căn hộ nhỏ gắn cờ 7,107 dòng (2.3%). Loại chúng, chênh lệch Cao − Thấp ở cửa sổ T1 đổi từ **+8.80 thành +9.63** điểm %: kết luận không đổi, nên là một dòng độ nhạy rẻ tiền.

**C6. Bước scaling không tạo ra kết quả (kỹ thuật #19a).** Ma trận Spearman tính trên giá trị gốc và trên giá trị min-max lệch nhau **0.0**; ma trận Pearson lệch ~1e-15. `zscore` được định nghĩa (MAIN §3.3) nhưng không gọi lần nào.

**C7. Nhất quán giữa file 2018 và các năm sau (Day 3: "không nhất quán" + "lỗi thời").**

| Chỉ số (toàn NSW) | 2018 (bản sao UAT) | 2021 | 2023 |
|---|---|---|---|
| Tỷ lệ mã `U` | **7.3%** | 3.6% | 2.5% |
| Tỷ lệ căn hộ `F` | **46.7%** | 54.1% | 48.6% |
| Thiếu tiền thuê (chung) | **3.82%** | 2.11% | 1.47% |

File 2018 chất lượng thấp hơn và có cơ cấu mã khác. Vì cả mốc 2018 lẫn mọi so sánh "thay đổi từ 2018" dựa trên nó, đây là rủi ro thật cho khâu so sánh. Điểm giảm nhẹ: trung vị 2018 khớp số DCJ chính thức (tương quan 0.996) **[V]**, và tỷ trọng `f01` trong nhóm so sánh chỉ lệch 20.1% so với 22.7% (2021).

**C8. Điều không phải vấn đề (để khỏi sửa thừa).** 8 cột khóa của bảng phân tích có **0 giá trị thiếu** sau toàn bộ chuỗi `merge`; 17.6% dòng thuộc postcode chia giữa hai SA4 (đã được xử lý bằng tỷ lệ phân bổ). Tệp `data/7a_504_foia_data_dictionary.xlsx` là từ điển dữ liệu **khoản vay SBA của Mỹ**, không liên quan dự án và không được tham chiếu ở đâu: đúng nghĩa "dữ liệu không liên quan" (Day 3 vấn đề #5).

---

## 5. PHẦN D. Hướng hoàn thiện, xếp theo ưu tiên (gắn với kiến thức bài giảng)

| # | Việc cần làm | Kiến thức bài giảng | Bằng chứng | Công sức | Ảnh hưởng tới kết luận |
|---|---|---|---|---|---|
| **P1** | Thêm mục **"mẫu thiếu dữ liệu"**: `isna().any/all(axis=1)`, tỷ lệ thiếu theo mã loại nhà và theo năm, biểu đồ cột mức đầy đủ. Viết ra lý do loại là an toàn vì thiếu dồn vào mã `U`. Áp khung 5 câu hỏi cho dữ liệu thiếu | Day 2 (null, `any/all`, biểu đồ cột), Day 3 (mẫu thiếu, khung 5 câu hỏi) | C1 | Thấp | Không đổi; tăng độ bảo vệ khi bị chất vấn |
| **P2** | **Điều tra outlier trước khi loại:** in hồ sơ các dòng bị loại (C3); bỏ `showfliers=False` ở §2.1 (hoặc thêm bản có outlier); thêm IQR **theo nhóm** (phân khúc × năm) làm dòng độ nhạy | Day 2 (điều tra outlier), Day 3 (boxplot theo nhóm, IQR) | C3, C5 | Thấp | Không đổi (T1: +8.80 → +9.63) |
| **P3** | **Dùng hoặc bỏ phần scaling.** Dùng: xây **chỉ số exposure tổng hợp = trung bình z-score của E2 và E4** (cần cho Quyết định 3). Hoặc bỏ §3.3 và xóa `zscore` | Day 3 (min-max, z-score, hàm) | C6 | Thấp | Làm bước scaling có chức năng thật |
| **P4** | **Kiểm tra nhất quán 2018 với các năm sau** trước khi dùng làm mốc: so cơ cấu mã loại nhà, tỷ lệ thiếu; chạy lại kết quả với mốc DCJ (2018) hoặc chỉ giữ dòng `F/H/T/O` | Day 3 ("không nhất quán", "lỗi thời"), Day 4 (`groupby` so sánh cơ cấu) | C7 | Thấp-TB | Có thể đổi các cửa sổ T0 và "tích lũy từ 2018" (vốn đã mong manh) |
| **P5** | **Đóng gói một hàm làm sạch duy nhất** (`clean_bond(df, rent_range, bed_range)`) dùng chung cho notebook và `scripts/06`. Hiện quy tắc viết hai lần (SQL trong MAIN §3.1; hằng số `RENT_MIN/RENT_MAX/BED_MAX` ở `06_build_panel.py` dòng 19, 68-71), chỉ bảo vệ bằng `assert` số dòng | Day 3 (hàm, tái dùng) | [R] | Thấp-TB | Tránh sai lệch ngầm khi sửa quy tắc |
| **P6** | **Kiểm tra `merge`** bằng `validate=` và `indicator=True` trong `scripts/05`, `06` (khoảng 10 phép ghép); in `_merge.value_counts()`; `assert` không có dòng `left_only` ngoài dự kiến | Day 4 (`indicator`) | C8 (hiện chưa gây hại) | Thấp | Không đổi; phòng thủ |
| **P7** | **Biểu đồ cho phát hiện chính:** đường "chênh lệch Cao − Thấp theo quý" (như đường DCJ 2018-2022) cùng nhà 3-4 phòng ngủ làm placebo; mỗi biểu đồ có một câu kết luận làm tiêu đề | Day 1 bước 4; Day 4 chuỗi thời gian | `PRESENTATION_AND_DECISIONS.md` | Thấp-TB | Truyền đạt tốt hơn; placebo đổi cách diễn giải |
| **P8** | **Quy đổi AUD/tuần:** ví dụ +8.8 điểm % trên mốc $570 ≈ +$50/tuần; ghi rõ mốc tham chiếu | Day 1 bước 6 | `PROPOSAL_v2.md` §4.5 đã hứa; MAIN chưa có | Thấp | Ngôn ngữ business |
| **P9** | **Nêu giả thuyết tường minh** (dấu dự đoán và điều gì sẽ bác bỏ) cho từng RQ; ghi nhật ký số dòng mất ở mọi lần `dropna` (kể cả 1 dòng ở file 2018) | Day 1 bước 1; Day 2-3 (đếm) | C2 | Thấp | Bảo vệ tốt hơn |
| **P10** | **Hấp thụ nguồn bổ sung vào MAIN** theo 6 quyết định đã thẩm định (BP0019, DCJ, Census, Housing Audit) và **dọn tệp không liên quan** (`7a_504_foia_data_dictionary.xlsx`) | Day 1 bước 2 (vòng lặp) ; Day 3 (dữ liệu không liên quan) | `PRESENTATION_AND_DECISIONS.md`; C8 | TB | Nâng độ tin cậy |

**Thứ tự đề xuất:** P1-P3 trong một buổi (rẻ, đều là kỹ thuật bài giảng làm chưa tới); P4-P5 trước khi chạy lại với Census/BP0019; P6-P9 khi hoàn thiện; P10 sau khi chốt 6 quyết định.

---

## 6. Giới hạn của bản audit này

- Mức (Vượt/Đạt/Một phần/Chưa) là **phán đoán của tôi** dựa trên đối chiếu code và output đã lưu; tôi đã truy vết kỹ thuật bằng tìm kiếm văn bản trên file `.py` của hai notebook (kết quả được kiểm tay vì tìm kiếm chuỗi có thể báo nhầm, ví dụ `fillna`, `replace`).
- Tôi **không chạy lại** toàn bộ hai notebook; các con số [V] được tính độc lập từ bảng đã xử lý trong `data/processed/` và `data/raw/`.
- Bài giảng Day 1-4 không dạy mô hình hóa nâng cao (hồi quy, bootstrap); việc dự án vượt ở bước 5 là **điểm cộng ngoài phạm vi**, không bị trừ khi thiếu các mô hình khác (như hồi quy hedonic trong `PROPOSAL_v2.md`).
- Kết luận về mức độ "vượt" không đồng nghĩa nội dung nghiên cứu đã đúng: tính đúng của kết luận được thẩm định riêng trong `PRESENTATION_AND_DECISIONS.md`.
