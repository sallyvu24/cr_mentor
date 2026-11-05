# Thẩm định các đề xuất cải thiện EDA và những gì đã sửa trong notebook

**Đầu vào được thẩm định:** `EDA_PIPELINE_AUDIT.md` (P1–P10, bằng chứng C1–C8) và `PRESENTATION_AND_DECISIONS.md` (Phần B: 6 quyết định ở mục 13 của `00_data_extraction_overview`, các việc 7–11, bộ quy tắc B.8).
**Phạm vi sửa:** P1–P3 và 6 quyết định mục 13 (theo yêu cầu "sửa trước, nếu hợp lí"), cộng các việc kéo theo trực tiếp (placebo, hạ cấp kết quả tích lũy, cảnh báo đa so sánh, cách tính đồng thuận).
**Quy ước nguồn:** **[NB]** = output của notebook mới đã chạy (`notebooks/sydney_student_rent_eda.ipynb`); **[V]** = tôi chạy lại các script `verification/v1–v6` và bản sao `scripts/09` (sửa đường dẫn) trên dữ liệu trong repo; **[L]** = tài liệu học `materials_required/Python_EDA_Day_1-4.ipynb` (số cell).

---

## 0. Tóm tắt

| Câu hỏi | Trả lời |
|---|---|
| Số liệu trong hai file audit có đúng không? | **Đúng, tái lập được toàn bộ** [V]: C1, C3–C7 của audit pipeline và các bảng B.1–B.7 (script 09 cho cả 4 tổ hợp giai đoạn × thước đo, v1–v5). Một ngoại lệ về diễn giải: C2 (xem A.2). |
| Đề xuất nào giữ nguyên? | P1, P2 (phần điều tra dòng bị loại), Quyết định 1–6, việc 7–9 và 11. |
| Đề xuất nào phải sửa trước khi làm? | **C2** (dòng "bị mất" ở file 2018 là dòng trống, không phải hợp đồng); **P2/C5** (IQR "theo năm" lặp lại lỗi của IQR toàn cục, phải áp theo ô postcode × phân khúc × giai đoạn); **P3** (chỉ số tổng hợp z-score mâu thuẫn với B.3–B.4, thay bằng cách dùng scaling có chức năng thật); **việc 7** (nhà ở *có* hồi một phần khi chia theo Census); **việc 11** (đổi quy tắc sau khi thấy kết quả, nên phải báo cáo cả quy tắc gốc). |
| Kết luận chính có đổi không? | **Hạng bằng chứng vẫn là B** ở cả 6 đặc tả (2 cách chia giai đoạn × 2 thước đo × quy tắc gốc/sửa) [NB]. Thay đổi về nội dung: nhịp hồi T1 của căn hộ nhỏ là **+10.0 điểm %** (trước +8.8); kết quả tích lũy **không còn là phát hiện**; nhịp sụt được placebo xác nhận là **của cả khu**; hành lang "vượt đều" giờ chỉ còn Parramatta (khu xa campus). |

---

## 1. Cách kiểm chứng

1. Chạy lại notebook chính **chưa sửa** trong môi trường cùng phiên bản (pandas 3.1.0, numpy 2.5.4, duckdb 2.0.0, geopandas 1.2.0): **mọi output dạng văn bản trùng khớp 100%** với bản đã lưu. Đây là mốc để so sánh trước/sau.
2. Chạy lại `verification/v1–v6` và `scripts/09` (bản sao với đường dẫn tương đối): mọi con số trích trong hai file audit đều tái lập được.
3. Đối chiếu từng đề xuất với tài liệu học: Day 2 (null `isnull().sum()` cell 177, biểu đồ mức đầy đủ cell 190–193, `any/all(axis=1)` cell 214–238, lọc và đọc dòng lạ cell 293–306, boxplot cell 320–325), Day 3 (7 vấn đề chất lượng cell 3, khung 5 câu hỏi cell 4, `fillna` bằng trung vị nhóm cell 29–37, boxplot theo nhóm cell 45, IQR cell 48–68, min-max và z-score cell 69–87, log cell 152–163), Day 4 (`merge` + `indicator` cell 69–72) [L].
4. Sửa notebook, chạy lại từ đầu đến cuối (khoảng 2 phút 15 giây, không lỗi), đọc lại mọi output và biểu đồ.

---

## 2. Phần A. Đề xuất của `EDA_PIPELINE_AUDIT.md`

### A.1 P1: mẫu thiếu dữ liệu (C1) → **Làm, có bổ sung**
- **Chẩn đoán đúng** [V]: thiếu tập trung ở mã `U`; giảm dần theo năm.
- **Lập luận của audit chưa đủ:** "mã `U` rơi vào nhóm `other` nên loại là an toàn" chỉ nói về `U`. Điều kiện thật để việc loại *không* tạo ra chênh lệch Cao − Thấp là: **tỷ lệ bị loại trong căn hộ phải như nhau giữa các nhóm exposure trong cùng giai đoạn**. Tôi kiểm tra trực tiếp điều này.
- **Đã thêm vào notebook (mục 2.1 và 3.6)** [NB]:
  - `isna().any/all(axis=1)` trên cả hai file: 81,818 dòng có ít nhất một ô thiếu (3.69%), 35,397 thiếu cả hai.
  - Theo loại nhà: `U` chỉ là 3.9% số hợp đồng nhưng chứa **83% số dòng thiếu tiền thuê** và 62% số dòng thiếu số phòng ngủ; căn hộ `F` chỉ thiếu 0.33% và 1.24%.
  - Theo năm (gồm cả file 2018): thiếu tiền thuê 3.82% (2018) → 2.11% (2021) → 1.00% (2026); file 2018 thiếu số phòng ngủ 8.05% và có 7.33% mã `U`.
  - Biểu đồ cột mức đầy đủ (đúng dạng Day 2 cell 192).
  - **Khung 5 câu hỏi Day 3 áp cho dữ liệu thiếu.** Câu "sửa được không?" trả lời *không* có lý do: điền trung vị nhóm (Day 3 cell 34–37) sẽ chèn chính đại lượng đang đo (trung vị postcode × phân khúc) vào dữ liệu, làm ô trông lớn hơn và khoảng bất định hẹp hơn thực tế.
  - **Kiểm tra cân bằng (3.6):** chênh lệch Cao − Thấp về tỷ lệ căn hộ bị loại lớn nhất chỉ **0.48 điểm %** (E2) và **0.55** (E4) ở bất kỳ giai đoạn nào; tỷ lệ bị loại phụ thuộc năm của file (khoảng 4% năm 2018, 1% sau đó), không phụ thuộc exposure.

### A.2 C2: "mất dòng âm thầm" ở file 2018 → **Đính chính**
- Audit đúng là `dropna` loại 1 dòng và notebook không in số đó.
- **Nhưng dòng đó là dòng trống cuối file** (`,,,,`), không phải một hợp đồng [V]. Không có hợp đồng nào bị mất, nên câu "trái với tuyên bố mọi dòng bị loại đều được đếm" là nói quá.
- Đã sửa theo hướng phòng thủ: notebook in số dòng đọc/bỏ/giữ, `assert` rằng chỉ được bỏ dòng **trống hoàn toàn**, và in các giá trị không phải số (chỉ có `U`: 26,709 ô số phòng ngủ, 12,664 ô tiền thuê) [NB].

### A.3 P2: điều tra outlier trước khi loại (C3, C5) → **Làm, đổi cách chọn nhóm cho IQR**
- **Hồ sơ các dòng bị giới hạn cứng loại** (Day 2 cell 293–306: lọc đúng các dòng lạ rồi đọc) [NB]: 4,215 hợp đồng (0.19%) trên cả hai file. Dưới $100: 3,472 dòng, trung vị $60, 100 dòng bằng 0, 58% là mã `O`. Trên $5,000: 743 dòng, trung vị $6,300, 60% là nhà riêng. Chỉ **0.09% số hợp đồng căn hộ** bị loại. `assert` mới nối hồ sơ này với nhật ký làm sạch: bước "rent" = số thiếu + dưới $100 + trên $5,000.
- **Boxplot có outlier:** mục 2.1 giờ vẽ cả outlier, thống kê hộp tính trên thang log (khớp với IQR trên log rent) và có hai đường giới hạn $100/$5,000. **Không** sửa `showfliers=False` ở mục 6.1, vì ở đó mọi postcode đã được vẽ thành điểm bằng `stripplot`; vẽ thêm outlier là vẽ trùng.
- **IQR theo nhóm: không làm theo cách của C5.** C5 áp IQR "trong từng năm" trên mọi postcode. Tôi kiểm tra: quy tắc đó gắn cờ **3.9% căn hộ nhỏ City of Sydney so với 1.5% ở nơi khác** [NB], tức lặp lại đúng lỗi mà notebook đã nêu với IQR toàn cục (cắt phần đắt của thị trường cần nghiên cứu). Nhóm đúng là **ô postcode × phân khúc × giai đoạn**, nơi trung vị thực sự được tính: chỉ những dòng bất thường *so với thị trường của chính nó* mới có thể làm lệch trung vị đó. Kết quả (mục 8): gắn cờ 2.8%; T1 đổi từ +9.95 thành +9.12 điểm %; kết luận không đổi.

### A.4 P3: bước scaling (C6) → **Chẩn đoán đúng; cách chữa đề xuất không nên làm; đã làm cách khác**
- **Chẩn đoán đúng** [V][NB]: Spearman trên giá trị gốc và min-max lệch nhau đúng 0; tertile không đổi ở 0/247 postcode sau log + z-score; `zscore` chưa từng được gọi. Câu "dùng scaling để so sánh các biến thể" trong notebook cũ là **sai về logic**: các phép theo hạng không cần scaling.
- **Không làm chỉ số tổng hợp "trung bình z-score của E2 và E4"**, vì:
  1. Nó mâu thuẫn với chính kết luận B.3–B.4 của file thẩm định: báo cáo E2 và E4 song song, và *không thêm thước đo thứ ba* vì làm tăng số "đường rẽ" để chọn kết quả.
  2. Cả hai biến đều lệch phải mạnh (độ lệch E2 1.30, E4 3.53 trong 117 postcode) [NB]: z-score trên giá trị gốc bị đuôi chi phối.
- **Đã làm (mục 3.3):** (a) kiểm chứng tường minh rằng Spearman và tertile bất biến với scaling, sửa lại câu giải thích; (b) dùng **log rồi z-score** (Day 3 cell 77, 131, 153) ở chỗ scaling thực sự cần: đặt E2 và E4 lên cùng thang để so từng postcode. Kết quả có ý nghĩa: Balmain 2041, Pyrmont 2009, Potts Point 2011, Rozelle 2039 *gần campus nhưng ít sinh viên sống*; Strathfield 2135, Burwood 2134 (khoảng 12 sinh viên/100 dân), Hurstville 2220 *nhiều sinh viên nhưng xa campus*. Đây chính là bằng chứng E4 là một phép thử thật của E2.

### A.5 Các đề xuất còn lại (ngoài phạm vi sửa lần này)

| # | Thẩm định | Trạng thái |
|---|---|---|
| C4 | Đúng [V]; nhưng mọi dòng lệch đều nằm ngoài phân khúc phân tích (nhà `H` 0 phòng ngủ → `other`; căn hộ ≥5 phòng → `f3p`) | Chưa thêm; ảnh hưởng bằng 0 tới so sánh |
| P4 (C7) | Đúng; **đã làm một phần**: file 2018 có mặt trong bảng mẫu thiếu (2.1), khớp trung vị DCJ chính thức (tương quan 0.996; 92% ô lệch ≤ $10) và có tỷ lệ bị loại cân bằng giữa các nhóm (3.6) [NB] | Chưa chạy lại với riêng mã `F/H/T/O` |
| P5 | Đúng: quy tắc làm sạch vẫn viết hai lần (SQL ở 3.1 và hằng số trong `scripts/06`) | Chưa làm |
| P6 | Đúng nhưng chưa gây hại (C8). Các phép `merge` mới trong notebook đều có `validate=` | `scripts/05–06` chưa sửa |
| P7 | **Đã làm** cùng Quyết định 2 và placebo: biểu đồ chênh lệch Cao − Thấp theo cửa sổ × phân khúc × thước đo (6.4), đường quý DCJ (6.5) | Xong |
| P8 | Hợp lý (AUD/tuần) | Chưa làm |
| P9 | Một phần: đã in số dòng bỏ ở file 2018 | Chưa nêu giả thuyết tường minh cho từng RQ |
| P10 | **Đã làm** (Phần B). Tệp `7a_504_foia_data_dictionary.xlsx` đúng là không liên quan, nhưng tôi **không xóa** tệp của bạn | Chờ bạn quyết |

---

## 3. Phần B. Sáu quyết định (mục 13) và các việc 7–11 của `PRESENTATION_AND_DECISIONS.md`

| # | Đề xuất của file thẩm định | Kiểm chứng | Đã làm trong notebook |
|---|---|---|---|
| **1** | BP0019 làm giai đoạn chính, BP0015 là độ nhạy duy nhất | Đúng [V]: T1 +8.8 (visa cấp) và +10.0 (số có mặt); hạng B ở cả hai; theo quy tắc gốc, đồng thuận giảm 80% → **đúng 60%**, bỏ từng hành lang 100% → 87% | **Làm (3.6).** Ranh giới không còn là hằng số "ngầm": bảng thay đổi so với cùng quý năm trước được in ra, và `assert` kiểm tra đáy 12/2021, đỉnh 03/2025, tăng ≥ +15% suốt 09/2022–12/2023, giảm ≥ 5% mọi quý từ 09/2025. **Khác file thẩm định:** vẫn nạp BP0015 để tính lại mốc độ nhạy từ dữ liệu thay vì gõ tay hằng số |
| **2** | Dùng DCJ 1PN/2PN 2018–2022 với 4 điều kiện | Đúng [V]: tương quan 0.996–0.999; ô ẩn lệch về nhóm Thấp (1PN: Thấp 87%, Cao 99% quý có số liệu); độ dốc trước COVID 1PN −1.24 [−3.08; −0.06], 2PN +0.34 [−0.67; +1.02] | **Làm (6.5)**, đủ 4 điều kiện. Định nghĩa cố định là **độ dốc hồi quy trên 8 quý** thay vì "trung vị theo năm", vì chính file thẩm định cho thấy so sánh theo năm đổi kết quả tùy cách gộp năm. **Phát hiện mới:** độ trôi của căn 1PN chỉ có khi chia theo E2; theo E4 là −0.42 [−1.34; +0.55]. Nếu kéo dài 3 năm, độ trôi E2 tương đương khoảng −4 điểm %, tức **một phần** khoảng sụt T0 (−10.7) có thể đã có từ trước COVID |
| **3** | Thêm E4, báo cáo song song, khóa "hạng = hạng thấp hơn" | Đúng [V]: ρ 0.77 (247 postcode) và 0.50 (117); 49% cùng nhóm; E4 2PN T1 ≈ căn nhỏ | **Làm (3.3–3.5, 6).** Mọi bảng RQ3 có cả E2 và E4; hạng cuối = hạng thấp hơn |
| **4** | Chỉ G01, G02, G15, G37 | Đúng [V]: tỷ lệ hộ không gia đình (G33) tương quan 0.35 với E4 nhưng 0.73 với tỷ lệ thuê nhà | Không cần sửa code; ghi trong bảng nguồn |
| **5** | Housing Audit chỉ làm biểu đồ bối cảnh, 3 ràng buộc | Đúng [V]: 6,797 → 12,924 phòng (+90%) | **Làm (9.2)** với đủ 3 ràng buộc |
| **6** | Bỏ DA và Airbnb khỏi notebook chính, chuyển sang phụ lục | Đúng [V] | **Làm:** `notebooks/appendix_context_da_airbnb.ipynb` tái lập đúng hai bảng cũ. **Đính chính:** dòng "Share of DAs with a dwelling count: 100%" của notebook cũ gây hiểu lầm: 99.8% có giá trị nhưng **22.3% bằng 0** |
| 7 | Placebo nhà 3–4PN | Đúng theo E2 (T0 −7.8; T1 +0.0) [NB]. **Đính chính:** theo E4, nhà *có* hồi +3.1 [+0.1; +5.2]. Cách đọc đúng: "nhà hồi **ít hơn nhiều** so với căn hộ nhỏ" chứ không phải "nhà không hồi" | **Làm (6.4)** |
| 8 | Hạ cấp kết quả tích lũy | Đúng: −2.7 đến +1.1 điểm % qua 4 đặc tả, chỉ 1/4 không chứa 0 | **Làm**: chỉ mô tả. **Phát hiện mới:** với nhà 3–4PN, nhóm Cao tăng *chậm hơn* nhóm Thấp ở cả 4 đặc tả (−5.3 đến −7.8) |
| 9 | Cảnh báo đa so sánh | Hợp lý | **Làm** (6.7, 10.3): 30 khoảng 90% chỉ riêng bảng đầu mục 6 |
| 10 | Đường dẫn hard-code trong `scripts/08, 08a, 09, 10`; chưa có script cho bảng DCJ | Đúng | Bảng DCJ giờ do notebook tự sinh từ `processed/extracted/`. **Bốn script vẫn hard-code `/Users/chipi/...`**: chưa sửa |
| 11 | Tính đồng thuận chỉ trên cửa sổ có tín hiệu | Đúng về logic [V]: theo BP0019, cửa sổ T2 (ρ ≈ −0.1) chỉ có 20% đồng thuận và kéo trung bình xuống đúng 60% | **Làm, kèm minh bạch.** Đổi quy tắc sau khi thấy kết quả là một "đường rẽ", nên notebook báo cáo **cả quy tắc gốc**: B (60%) với giai đoạn chính và B (80%, đúng kết quả bản cũ) với giai đoạn visa cấp. Hai quy tắc cho cùng hạng |

**Bộ quy tắc B.8:** cả 6 quy tắc được áp dụng. Quy tắc 3 được hiện thực bằng **bảng 4 đặc tả** ở mục 6.7. Chỉ 4 kết quả đạt điều kiện "phát hiện": căn hộ nhỏ T0 (sụt) và T1 (hồi), nhà 3–4PN T0 (sụt) và tích lũy.

**Một điểm file thẩm định chưa nêu:** với giai đoạn visa cấp và E4, có 2 cửa sổ không chứa 0 (T1 và T2, cận dưới +0.2), tức đủ số cửa sổ cho hạng A. Hạng vẫn là B vì chỉ 64% định nghĩa khác đồng thuận ở hai cửa sổ đó. Notebook ghi rõ điều này, vì đây chính là kịch bản "lên A nhờ một biên 0.1 điểm %" mà file thẩm định cảnh báo.

---

## 4. Phần C. Thay đổi theo từng mục của notebook chính

| Mục | Thay đổi | Đề xuất |
|---|---|---|
| Đầu notebook | Bảng nguồn (thêm Census, BP0019, DCJ, Housing Audit; DA/Airbnb chuyển phụ lục); quy tắc xếp hạng có ghi chú sửa đổi ngày 05/11/2026 | QĐ 1–6, việc 11 |
| 2.1 | Đọc file 2018 ngay ở phần hiểu dữ liệu (đếm dòng bỏ, `assert` dòng trống); mẫu thiếu dữ liệu + khung 5 câu hỏi; hồ sơ dòng bị giới hạn cứng loại; boxplot có outlier | P1, C2, P2 |
| 2.2–2.3 | Hồ sơ chất lượng cho BP0019, Census, DCJ, Housing Audit; bảng tóm tắt chất lượng cập nhật | QĐ 2–5 |
| 3.1 | `assert` nối nhật ký làm sạch với hồ sơ dòng bị loại | P2 |
| 3.3 | Scaling viết lại: kiểm chứng bất biến theo hạng; log + z-score so E2 với E4 | P3 |
| 3.4–3.5 | Mô tả E4; bản đồ E4; tertile theo E4; bảng chéo E2 × E4 | QĐ 3 |
| 3.6 | Giai đoạn theo BP0019 (chính) và BP0015 (độ nhạy); kiểm tra cân bằng dòng bị loại | QĐ 1, P1 |
| 4–5 | Nhãn giai đoạn mới; câu kết luận sinh từ số liệu | QĐ 1 |
| 6 | Kết quả theo E2 và E4 cho căn nhỏ, 2PN, nhà 3–4PN; 6.4 placebo + biểu đồ chính; 6.5 kiểm tra trước COVID bằng DCJ; 6.6 lưới 8 định nghĩa exposure; 6.7 bảng 4 đặc tả, hạng theo quy tắc sửa và quy tắc gốc | QĐ 1–3, việc 7–9, 11, P7 |
| 8 | Thêm dòng độ nhạy: E4, giai đoạn visa cấp, IQR trong ô, bỏ dòng trùng | P2, QĐ 1 |
| 9 | 9.2 Housing Audit; 9.3 "những gì dữ liệu không kiểm định được" | QĐ 5–6 |
| 10 | Phát hiện, khuyến nghị, giới hạn, kết luận viết lại và sinh từ số liệu | Tất cả |

Tệp khác: `appendix_context_da_airbnb.ipynb/.py/.html` (mới); mục 13 của `00_data_extraction_overview` ghi lại các quyết định đã chốt (chỉ sửa markdown, output giữ nguyên); `DATA_README.md`; một dòng chú thích trong `scripts/06_build_panel.py` (không đổi logic, không tạo lại dữ liệu).

---

## 5. Phần D. Kết quả trước và sau khi sửa

| Chỉ số (căn hộ nhỏ, Cao − Thấp, điểm %) | Notebook cũ (visa cấp, E2) | Notebook mới: số có mặt, E2 | Số có mặt, E4 |
|---|---|---|---|
| T0: 2018 → đóng cửa | −10.4 [−13.9; −5.5] | −10.7 [−14.0; −5.2] | −6.6 [−12.2; −4.1] |
| **T1: đóng cửa → hồi phục** | **+8.8 [+5.1; +11.1]** | **+10.0 [+7.3; +12.8]** | **+10.0 [+6.2; +13.3]** |
| T2 | +0.9 [−2.3; +3.7] | −3.7 [−5.4; +1.5] | +0.0 [−3.4; +3.0] |
| T3 (với giai đoạn mới: đi ngang → giảm) | −0.8 [−2.8; +0.1] | +0.0 [−1.0; +2.0] | +0.0 [−1.2; +1.5] |
| Tích lũy 2018 → giai đoạn cuối | −2.7 [−7.3; −0.2] (*phát hiện*) | −2.7 [−6.7; +0.5] | −0.5 [−2.2; +3.2] (*chỉ mô tả*) |
| Hạng bằng chứng | B | B | B → **hạng cuối B** |
| Hành lang "vượt đều" (≥5/6) | Merrylands-Guildford, Ryde-Hunters Hill | Parramatta (xa campus) | – |

Bảng độ nhạy (mục 8, E2, giai đoạn chính): T1 nằm trong khoảng **+8.8 đến +11.3** ở mọi kịch bản (ô tối thiểu 30/60/100, bỏ City of Sydney, nhóm tứ phân vị, E4, giai đoạn visa cấp, IQR trong ô, bỏ dòng trùng) [NB].

---

## 6. Phần E. Các con số trong kịch bản thuyết trình (`PRESENTATION_AND_DECISIONS.md`, Phần A) cần cập nhật

Kịch bản viết theo notebook cũ. Sau khi đổi giai đoạn chính sang BP0019 [NB]:

| Slide | Đang ghi | Nên sửa thành |
|---|---|---|
| 5, ý 1 | City of Sydney căn nhỏ $570 → $480 → $775 (+36%); 2PN $780 → $650 → $1,100 (+41%) | $570 → $480 → **$799 (+40%)**; 2PN $780 → $650 → **$1,150 (+47%)**; giai đoạn cuối là 07/2025–09/2026. Mọi nhóm căn nhỏ đều khoảng **+40%** |
| 5, ý 2 | Sụt sâu hơn 10.4, hồi mạnh hơn 8.8, sau đó +0.9 và −0.8 | Sụt 10.7 (E4: 6.6), hồi **10.0** (E4: 10.0), sau đó −3.7 và +0.0 (khoảng đều chứa 0). Thêm: nhà 3–4PN cũng sụt 7.8–8.3 nhưng hồi ít (0.0 đến +3.1) |
| 5, ý 3 | Hai hành lang vượt đều: Merrylands-Guildford, Ryde-Hunters Hill | Chỉ **Parramatta** (mean E2 6.0), vẫn là khu xa campus |
| 7, ý 1 | Placebo "không hồi (T1: −0.1)" | "Hồi ít hơn nhiều": E2 +0.0, E4 +3.1 [+0.1; +5.2] |
| 7, ý 5 | "Gần song song (trong ~2 điểm %/năm)" | Giữ; thêm: độ trôi 1PN chỉ xuất hiện khi chia theo E2 |

---

## 7. Phần F. Việc còn lại (chưa làm, có chủ ý)

1. **P5, P6:** đóng gói quy tắc làm sạch thành một hàm dùng chung; thêm `validate`/`indicator` cho các `merge` trong `scripts/05–06`.
2. **Việc 10:** sửa đường dẫn hard-code trong `scripts/08_parse_dcj_rent.py`, `08a_…`, `09_…`, `10_…`.
3. **P8:** quy đổi khoảng chênh lệch ra AUD/tuần cho người đọc business.
4. **P9:** nêu giả thuyết tường minh (dấu dự đoán, điều gì bác bỏ) cho từng RQ.
5. **C4:** liệt kê các dòng lệch chéo trường trong bảng chất lượng (không ảnh hưởng phân khúc phân tích).
6. **Tệp không liên quan** `7a_504_foia_data_dictionary.xlsx`: chờ bạn quyết có xóa không.
7. Cập nhật kịch bản thuyết trình theo Phần E; `PROPOSAL_v2.md` và `PROJECT_BRIEF.md` vẫn còn số cũ (việc 9 của file thẩm định).

## 8. Giới hạn của lần thẩm định này

- Ranh giới giai đoạn theo BP0019 (ngưỡng +15% và −5%) là **phán đoán**, được ghi rõ và kiểm tra bằng `assert`. Dòng độ nhạy theo visa cấp là để kiểm tra phán đoán đó. T1, cửa sổ duy nhất có tín hiệu, chỉ phụ thuộc đáy 11–12/2021 mà cả hai chuỗi đều đồng ý.
- Việc sửa quy tắc đồng thuận (việc 11) được làm **sau khi** đã biết kết quả. Vì vậy notebook giữ song song kết quả theo quy tắc gốc; cả hai cho hạng B.
- Khoảng bootstrap dựa trên khoảng 20 cụm SA3, nên các cận sát 0 (ví dụ +0.1, +0.2) không ổn định; không kết luận nào dựa trên chúng.
- Notebook overview **không được chạy lại** (cần tải lại từ các trang nguồn); chỉ phần markdown của mục 13 được sửa và HTML được xuất lại từ output đã lưu.

**Chạy lại:** từ `data/notebooks/`: `jupyter nbconvert --to notebook --execute --inplace sydney_student_rent_eda.ipynb` (khoảng 2–3 phút; cần `processed/extracted/` từ notebook overview). Các script kiểm chứng: `cd data/verification && python3 v1_dcj_checks.py` (tương tự cho v2–v6).
