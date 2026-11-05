# Đánh giá mức độ hoàn thiện về lập luận của notebook EDA chính (phiên bản hiện tại)

**Vai trò đánh giá:** senior data analyst; đánh giá *chuỗi suy luận*: mỗi section có (a) mục đích trong pipeline, (b) phương pháp EDA, (c) phát hiện, (d) bằng chứng ở section đó có đỡ nổi phát hiện không.
**Đối tượng:** `notebooks/sydney_student_rent_eda` **sau đợt sửa ngày 05/11/2026** (commit `c1b9f7a`: giai đoạn theo BP0019, thước đo Census E4, placebo nhà, kiểm tra DCJ, quy tắc xếp hạng sửa, DA/Airbnb chuyển phụ lục). Số mục theo notebook hiện tại.
**Quy ước:** **[NB]** = output đã lưu của notebook; **[V]** = tôi tính lại bằng `data/verification/v7_argument_checks.py` (trên cấu hình cũ) và `v8_current_notebook_checks.py` (trên cấu hình hiện tại).

> **Lưu ý về phiên bản.** Bản đánh giá đầu tiên của tôi (commit `59570ff`) mô tả notebook *trước* đợt sửa. Bản này thay thế nó. Mục 3 ghi rõ phát hiện nào đã được xử lý, còn lại, hoặc cần đính chính.

**Thang:** **Chặt** = bằng chứng đỡ trực tiếp, giả định được nêu và kiểm; **Khá** = đúng hướng, còn một giả định chưa kiểm hoặc chưa nêu; **Hở** = phát biểu mạnh hơn bằng chứng; **Yếu** = phép thử không phân biệt được hoặc không tạo ra kết quả.

---

## 0. Kết luận tổng

**Mức hoàn thiện lập luận hiện tại: tốt, khoảng 8/10** (bản trước sửa: ~7/10).

- **Điều đã làm tốt hơn hẳn:** (1) kết luận cuối vẫn hiệu chỉnh đúng với bằng chứng; (2) *phát hiện* được định nghĩa bằng tiêu chí chặt: một cửa sổ chỉ là phát hiện khi khoảng 90% loại trừ 0, **cùng dấu, dưới cả hai thước đo exposure và cả hai cách chia giai đoạn**; (3) có **kiểm định phân biệt** (placebo nhà 3-4PN, kiểm tra xu hướng trước COVID bằng DCJ, thước đo Census độc lập); (4) thay đổi quy tắc xếp hạng sau khi thấy kết quả được **thừa nhận và báo cáo song song với quy tắc gốc**.
- **Điều còn hở:** hai kết quả phụ vẫn không đứng vững (**mùa vụ**, **danh sách hành lang RQ4**) và vẫn xuất hiện trong mục Phát hiện chung (10.1); còn thiếu **bảng giả thuyết cạnh tranh có dự đoán khác biệt**, nên phần "không tách được" chưa phải kết luận được kiểm trực tiếp.
- **Điểm tôi đính chính ở phiên bản trước:** mất cân bằng nền giữa hai nhóm **không còn là lỗ hổng lớn** (xem 3.5 dưới đây).

---

## 1. Bản đồ pipeline → phương pháp → phát hiện, theo từng section

### 1.1 Luồng tổng thể

```
Hỏi (RQ1-4, quy tắc xếp hạng đặt trước)
  → Hiểu và kiểm tra dữ liệu (§2)  → Làm sạch + dựng bảng (§3.1-3.2)
  → Dựng 2 thước đo exposure E2/E4, chọn nhóm so sánh, định nghĩa giai đoạn (§3.3-3.6)
  → Mô tả (RQ1 §4, RQ2 §5) → Kiểm định liên hệ (RQ3 §6: so nhóm, placebo, trước COVID, xếp hạng)
  → Ưu tiên (RQ4 §7) → Độ bền (§8) → Giải thích khác (§9) → Phát hiện, khuyến nghị (§10)
```

### 1.2 Bảng chi tiết

| Section | Mục đích | Phương pháp EDA | Phát hiện | Lập luận | Điều còn lại |
|---|---|---|---|---|---|
| **Mở đầu** (RQ, phạm vi, quy tắc xếp hạng) | Đặt luật chơi trước kết quả | 4 RQ; hạng A/B/C; hạng cuối = hạng thấp hơn của E2 và E4; "phát hiện" = lặp lại ở 4 đặc tả | Quy tắc rõ, có ghi chú sửa đổi 05/11 | **Chặt** | Giả thuyết còn ngầm (không có dự đoán dấu và điều bác bỏ). Ngưỡng 60%/80% là tùy ý. "Cửa sổ có tín hiệu" chọn theo chính kết quả, nên 100% đồng thuận một phần là hệ quả của việc chọn |
| **§2.1-2.3** Hiểu dữ liệu | Biết dữ liệu trước khi giả định | `info/describe`, mẫu thiếu (`any/all(axis=1)`, theo mã nhà và năm), hồ sơ dòng bị loại, trùng, IQR so với giới hạn cứng, SQL theo tháng | Thiếu dồn vào mã `U` (83% thiếu tiền thuê); 0.09% hợp đồng căn hộ bị giới hạn cứng loại; file năm = file tháng | **Chặt** | Đã xử lý các lỗ hổng bản trước. Còn: đoạn "thứ trong tuần" không phục vụ kết luận nào |
| **§3.1-3.2** Làm sạch, bảng phân tích | Bảng sạch, có kế toán | SQL + nhật ký đếm; `assert` nối nhật ký với hồ sơ dòng bị loại | 2,215,281 → 2,129,444 → 1,484,734 | **Chặt** | Giới hạn $100-$5,000 nay có bằng chứng đi kèm (hồ sơ dòng bị loại) |
| **§3.3** Scaling | Đưa các thước đo lên cùng thang | Kiểm chứng Spearman và tertile bất biến; log + z-score để so E2 với E4 từng postcode | Postcode "gần campus nhưng ít sinh viên sống" và ngược lại | **Chặt** | Bước này nay có chức năng thật |
| **§3.4** Dựng exposure | Mắt xích trung tâm của cả phân tích | E2 (campus × ghi danh × khoảng cách), E3, E1; **thêm E4 (Census)** | E2 và E4 là hai đại lượng khác nhau | **Khá** | **Giả định thời gian không đổi** vẫn chưa nêu: ghi danh 2025 và Census 2021 dùng để giải thích thay đổi 2018-2021. Cả hai đo nơi học hoặc nơi ở của *mọi* sinh viên đại học, không riêng sinh viên quốc tế |
| **§3.5** Nhóm so sánh | Có nhóm đối chứng hợp lý | Tertile theo E2 và theo E4; bảng chéo; "so thay đổi, không so mức" | Chỉ 49% postcode cùng nhóm giữa E2 và E4 | **Khá** | Xem mục 3 (đính chính): E4 *cân bằng* giá nền; 13/39 postcode nhóm Cao (E2) là City of Sydney |
| **§3.6** Giai đoạn | Cắt thời gian thành cửa sổ so sánh | BP0019 (số có mặt, chính) với `assert` đáy/đỉnh/ngưỡng +15%/−5%; BP0015 làm độ nhạy | Hai chuỗi cùng đồng ý đáy 11-12/2021; khác đỉnh | **Khá chặt** | Ngưỡng +15% và −5% là phán đoán (được ghi và `assert`). T0 trải 2018→2021, trong khi DCJ cho thấy khoảng cách mở từ 2020Q2 |
| **§4.1-4.3** RQ1: chuyện gì xảy ra | Mô tả nhịp chung | Chỉ số trung vị theo tháng, bảng trung vị theo giai đoạn, pandas = SQL | Căn hộ nhỏ ≈ +40% so với 2018 ở *mọi* nhóm; nhịp chung chi phối **tích lũy** | **Khá chặt** | 10.1 đã giới hạn câu "chênh lệch nhỏ" cho *tích lũy*, đúng. RQ1 dùng trung vị gộp hợp đồng, RQ3 dùng trung vị theo postcode: hai ước lượng "thay đổi" khác trọng số, chưa đối chiếu. 80% rent là bội của $10 (một bước $10 = 2.2% ở mốc $450) nên chênh lệch 1-3 điểm % ở T2, T3, tích lũy nằm trong độ phân giải |
| **§4.4** Mùa vụ | Có "dấu vân tay" lịch học? | Log trung vị gộp − trung bình trượt 12 tháng; trung bình theo tháng; Cao − Thấp | Tháng 2: Cao +4.1% so với Thấp +0.4%; dương 4/5 năm | **Hở** | **Không đổi so với bản cũ.** **[V]** tách xu hướng theo *từng postcode* thì chênh lệch còn **+1.4 điểm %** (căn nhỏ), nhỏ hơn một bước làm tròn; "4/5 năm dương" có xác suất 19% nếu không có hiệu ứng. Được thêm sau khi đã thấy kết quả. Mục 10.1 #6 lặp lại con số này **không kèm cảnh báo** |
| **§5** RQ2: ở đâu | Mô tả không gian | Thay đổi log theo postcode (≥30 hợp đồng), bản đồ, trung vị theo hành lang | 20/20 hành lang tăng, +26% đến +41%; Inner City +30%, hạng 15/20 | **Khá** | "Lan rộng" được đỡ tốt. Nội thành tăng *ít hơn* phần lớn hành lang (hạng 15/20) chính là câu chuyện "sụt sâu, hồi chưa bù hết" của RQ3 nhưng văn bản chưa nối hai điều này |
| **§6.0-6.3** RQ3: so nhóm | Có chênh lệch Cao − Thấp không | Chênh lệch trung vị theo nhóm; **cluster bootstrap theo SA3**; Spearman; hoán vị (chỉ tham khảo); E2 và E4 | T0 −10.7 (E4: −6.6); **T1 +10.0 (E4: +10.0)**; T2, T3 ≈ 0 | **Khá chặt** | 6.3 nay thừa nhận "tính đặc thù của căn nhỏ không vững" (E2 +2.6, E4 −0.4). Số cụm mang nhóm Cao (xem 3.3 dưới đây) |
| **§6.4** Placebo nhà 3-4PN | Tách "khu" khỏi "sinh viên" | Cùng cửa sổ, cùng nhóm, phân khúc nhà riêng; biểu đồ tổng hợp | Nhịp **sụt cũng có ở nhà** (−7.6 đến −8.8); nhịp **hồi nhỏ hơn nhiều** | **Chặt** | **[V]** Có thể định lượng bằng tương phản căn hộ trừ nhà: T1 **+8.2 [+5.3; +10.5]** (E2), **+6.8 [+3.3; +9.5]** (E4): nhịp hồi *đặc thù căn hộ*, vững ở cả hai thước đo. T0: −1.5 [−5.3; +1.3] và −0.8 [−2.2; +3.6]: nhịp sụt *không* đặc thù căn hộ |
| **§6.5** Trước COVID (DCJ) | Hai nhóm có đi song song trước COVID không | Độ dốc hồi quy 8 quý, có khoảng bất định; bản cân bằng; đối chiếu với bond | "Gần song song, không phải song song": tối đa 1.4 điểm %/năm; khoảng cách mở sau khi biên giới đóng, khép vào 2022Q4 | **Chặt** | Định nghĩa cố định, tránh nhạy cảm cách gộp năm. Đoạn ngoại suy "−4 điểm % sau 3 năm" giả định xu hướng tuyến tính; với E4 độ trôi chỉ −0.42/năm (≈ −1.3 sau 3 năm), nên nên nêu *khoảng* −1.3 đến −4 thay vì một số |
| **§6.6-6.7** Độ bền, hạng | Ra hạng bằng chứng | 8 định nghĩa exposure × cửa sổ; bỏ từng hành lang; bảng 4 đặc tả; hạng theo quy tắc sửa **và** quy tắc gốc | Hạng **B** ở cả 4 tổ hợp; chỉ 4 cửa sổ là phát hiện | **Chặt** | 6/8 định nghĩa exposure là biến thể của E2, nên với tiers E2 "đồng thuận" gần như tautology; chính **tiers E4 + quy tắc "hạng thấp hơn"** mới là phép kiểm có nghĩa. Ngưỡng và "cửa sổ có tín hiệu" chọn theo kết quả |
| **§7** RQ4: hành lang | Ưu tiên hóa | Trung vị hành lang so với trung vị nhóm Thấp; "nhất quán" = trên chuẩn ≥5/6 | Chỉ Parramatta vượt đều (khu xa campus) | **Yếu** | **[V]** Quy tắc **không phân biệt được với ngẫu nhiên**: với nhãn hành lang hoán vị ngẫu nhiên, trung bình **1.1 hành lang** vượt ngưỡng; quan sát được **1**; xác suất ngẫu nhiên cho ≥1 là **70%**. Xác suất "không hành lang nào trong 6 hành lang exposure cao vượt" nếu chỉ do ngẫu nhiên: **71%**. Cả "Parramatta" lẫn "không hành lang gần campus nào" đều không mang thông tin |
| **§8** Độ bền | Kết quả có đổi theo lựa chọn không | Ngưỡng 30/60/100; bỏ City of Sydney; tứ phân vị; **E4; giai đoạn visa; IQR theo ô; bỏ trùng** | T1 trong khoảng +8.8 đến +11.3 ở mọi kịch bản | **Chặt** | Khác bản cũ: nay *đổi giả định*, không chỉ đổi tham số |
| **§9** Giải thích khác | "Còn giải thích nào khác?" | Cấu trúc nền theo hai cách chia; Housing Audit (bối cảnh); **9.3 "những gì dữ liệu không kiểm được"** | Supply và Airbnb: đã xem, không kiểm được | **Khá** | Trung thực. Nhưng giả thuyết cạnh tranh *chính* (làm việc từ xa, du lịch, văn phòng nội thành) chỉ xuất hiện trong lời cảnh báo, chưa được liệt kê kèm dự đoán |
| **§10** Phát hiện, khuyến nghị, giới hạn | Truyền đạt | Văn bản sinh từ số liệu; khuyến nghị theo hạng | 7 phát hiện, 6 khuyến nghị | **Khá chặt** | #1-#5 vững. **#6 (mùa vụ) và #7 (hành lang)** dựa trên hai kết quả yếu ở trên. Giới hạn đã bổ sung nhiều (phong tỏa 2021, đa so sánh, nhãn giai đoạn) nhưng còn thiếu: làm tròn $10, tương phản căn hộ trừ nhà, giả định thời gian không đổi của exposure. Khuyến nghị chưa quy ra AUD/tuần |

---

## 2. Chuỗi suy luận chính: 4 mắt xích, tình trạng hiện tại

```
Dữ liệu sạch → [L1] E2/E4 đo "sinh viên ở khu" → [L2] nhóm Cao/Thấp so sánh được
  → [L3] cửa sổ thay đổi có nghĩa → T0/T1 có chênh lệch → [L4] chênh lệch là của "sinh viên"
```

| Mắt xích | Bản trước | Hiện tại | Bằng chứng |
|---|---|---|---|
| **L1** exposure đo sinh viên | Chưa kiểm độc lập | **Đã kiểm một phần** (E4 độc lập với E2); kết quả T1 lặp lại ở hai thước đo | T1 +10.0 ở cả E2 và E4 [NB]; tương quan hạng E2-E4 chỉ 0.50 trong nhóm so sánh |
| **L2** nhóm so sánh được | Nghi ngờ do nền không cân bằng | **Phần lớn được bảo vệ** | **[V]** Tiers E4 *cân bằng nền* (trung vị nền $498 so với $482) mà T1 vẫn +10.0. Với E2, tương quan hạng T1 giảm rất ít khi kiểm soát giá nền và tỷ lệ căn hộ (+0.54 → +0.51; E4: +0.57 → +0.53), và quan hệ dương ở **cả ba tầng giá nền** (E2: +8.6/+3.6/+2.9; E4: +8.3/+6.5/+4.6) |
| **L3** cửa sổ có nghĩa | Phụ thuộc cắt giai đoạn | **Được kiểm** (hai cách chia giai đoạn; T1 chỉ phụ thuộc đáy 11-12/2021, hai chuỗi đồng ý) | §3.6, §8 |
| **L4** là của sinh viên | Chưa có phép phân biệt | **Thu hẹp, chưa đóng:** nhịp hồi *đặc thù căn hộ* (+6.8 đến +8.2, vững), nhịp sụt *đặc thù khu*. Nhưng "đặc thù căn hộ" không có nghĩa "do sinh viên": cú sốc cầu căn hộ nội thành nói chung (làm việc từ xa, du lịch, di cư) cũng ảnh hưởng căn hộ nhiều hơn nhà | Placebo và tương phản căn hộ trừ nhà; 6.3 |

**Nhận định:** kết luận hiện tại ("tín hiệu tạm thời, chưa tách được khỏi chu kỳ nội thành") nay **được hỗ trợ bằng kiểm định**, không chỉ là mặc định. Để đóng L4 cần một phép thử với dự đoán *khác nhau* giữa giả thuyết sinh viên và giả thuyết cú sốc nội thành (ví dụ: khu có campus nhưng ít văn phòng/du lịch; hoặc dữ liệu ngày bắt đầu hợp đồng).

---

## 3. Phát hiện của bản đánh giá trước, so với notebook hiện tại

| # | Phát hiện bản trước | Tình trạng | Ghi chú |
|---|---|---|---|
| 1 | Chưa có placebo | **Đã xử lý** | §6.4. Thêm: tương phản căn hộ trừ nhà để định lượng (3.1 dưới) |
| 2 | Kết quả tích lũy mong manh | **Đã xử lý** | Hạ xuống mô tả; ghi nhận nhà 3-4PN tăng chậm hơn |
| 3 | Chỉ số đồng thuận lẫn cửa sổ ρ≈0 | **Đã xử lý** | Tính ở cửa sổ có tín hiệu; quy tắc gốc báo cáo song song |
| 4 | Exposure cùng gốc, chưa kiểm độc lập | **Đã xử lý một phần** | E4; hạng = hạng thấp hơn |
| 5 | Chưa kiểm xu hướng trước COVID | **Đã xử lý** | §6.5 |
| 6 | DA/Airbnb không có chức năng suy luận | **Đã xử lý** | Chuyển phụ lục; §9.3 |
| 7 | Phép so căn nhỏ với 2PN có giả định không chắc | **Đã xử lý một phần** | Văn bản nay thừa nhận không vững; giả định hướng dự đoán vẫn chưa được biện minh |
| 8 | Mùa vụ bị phóng đại | **Còn nguyên** | §4.4 và 10.1 #6 không đổi |
| 9 | RQ4 không phân biệt được với ngẫu nhiên | **Còn nguyên** | **[V]** vẫn đúng với cấu hình mới (xem §7 trong bảng) |
| 10 | Làm tròn rent $10 | **Còn nguyên** | Không được nêu |
| 11 | Mất cân bằng nền giữa hai nhóm | **Đính chính: không còn là lỗ hổng lớn** | Xem L2 ở trên. Tôi đã đánh giá quá nặng ở phiên bản trước vì chỉ thử trên tiers E2 và giai đoạn cũ |
| 12 | Ít cụm mang nhóm Cao, CI có thể hẹp | **Đã giảm** | **[V]** Với E4, nhóm Cao trải trên **16/31** cụm (E2: 9/31), 5-6 cụm có ≥3 postcode. T1 vẫn +10.0 [+6.2; +13.3] ở E4, nên kết luận không phụ thuộc vào việc E2 chỉ có vài cụm |
| 13 | Giả thuyết cạnh tranh chưa liệt kê | **Còn nguyên** | Chưa có bảng dự đoán khác biệt |

### 3.1 Phát hiện mới: tương phản căn hộ trừ nhà (dùng chính placebo của notebook)

Notebook đọc placebo bằng lời ("nhà cùng chia sẻ nhịp sụt, ít hơn nhịp hồi"). Có thể thành một đại lượng có khoảng tin cậy: lấy chênh lệch Cao − Thấp của *căn hộ nhỏ* trừ chênh lệch Cao − Thấp của *nhà* trong cùng postcode **[V]**:

| Cửa sổ | Tiers E2 | Tiers E4 | Đọc |
|---|---|---|---|
| T0 (2018 → đóng cửa) | −1.5 [−5.3; +1.3] | −0.8 [−2.2; +3.6] | Nhịp sụt **không** đặc thù căn hộ |
| **T1 (hồi)** | **+8.2 [+5.3; +10.5]** | **+6.8 [+3.3; +9.5]** | Nhịp hồi **đặc thù căn hộ**, vững |
| Tích lũy | +3.9 [−1.7; +7.1] | +7.4 [+3.7; +10.0] | Căn hộ khu Cao tăng *nhiều hơn* nhà cùng khu (E4 loại trừ 0) |

Hàm ý: ở mức tích lũy, "không có chênh lệch" của căn hộ (−2.7 đến +1.1) che một điều: nhà ở khu Cao tăng chậm hơn nhà khu Thấp 5-8 điểm %, nên căn hộ khu Cao đang tăng *khá hơn mặt bằng khu của chính nó*. Thông điệp này cần cẩn trọng (vẫn phù hợp cả giả thuyết cầu căn hộ nội thành), nhưng nó làm cho kết luận "không có gì" **chính xác hơn**.

---

## 4. Việc còn lại để hoàn thiện lập luận (xếp theo tác động)

| # | Việc | Mắt xích | Công sức | Tác động |
|---|---|---|---|---|
| **B1** | **Bảng giả thuyết cạnh tranh** (sinh viên; làm việc từ xa/văn phòng; du lịch; di cư; cung) với *dự đoán khác biệt* và phép thử tương ứng; đưa tương phản căn hộ trừ nhà vào bảng 4 đặc tả | L4 | Thấp | Biến "không tách được" thành kết luận có cấu trúc |
| **B2** | **Hạ hoặc bỏ phát hiện mùa vụ**: dùng ước lượng theo postcode (+1.4 điểm %), nêu nhỏ hơn bước làm tròn; thêm cảnh báo vào 10.1 #6 | §4.4, §10 | Thấp | Loại một số liệu phóng đại |
| **B3** | **Thay RQ4 bằng bảng mô tả**, hoặc hiệu chỉnh ngưỡng bằng hoán vị; bỏ #7 khỏi phát hiện và bỏ "Parramatta" khỏi thông điệp | §7, §10 | Thấp | Loại một kết luận không có thông tin |
| **B4** | Nêu **giả định thời gian không đổi** của exposure (ghi danh 2025, Census 2021) và nêu rõ E4 đo *mọi* sinh viên đại học | §3.4, §10.3 | Thấp | Trung thực |
| **B5** | Nêu **bước làm tròn $10 = 2.2%** ở mốc $450 và đối chiếu RQ1 (trung vị gộp) với RQ3 (trung vị postcode) | §4, §10.3 | Thấp | Đặt đúng độ phân giải |
| **B6** | Ở 6.5, nêu độ trôi trước COVID thành **khoảng (−1.3 đến −4 điểm %)** thay vì một số | §6.5 | Thấp | Chính xác |
| **B7** | Nối RQ2 ("nội thành hạng 15/20") với RQ3 trong văn bản | §5 | Thấp | Mạch lạc |
| **B8** | Quy đổi AUD/tuần (+10 điểm % trên mốc $570 ≈ +$57/tuần) | §10 | Thấp | Ngôn ngữ business |
| **B9** | Biện minh hướng dự đoán của phép so căn nhỏ với 2PN, hoặc bỏ 6.3 (có thể thay bằng tương phản căn hộ trừ nhà) | §6.3 | Thấp | Bỏ phép thử không có hướng rõ |

**Thứ tự:** B1 trước (tác động lớn nhất lên L4); B2-B3 tiếp theo (loại hai kết quả yếu khỏi thông điệp); B4-B9 khi chỉnh văn bản.

---

## 5. Đính chính các nhận định trước của tôi

- **Số cụm bootstrap.** Ở các tài liệu trước tôi viết "~20 cụm". **Sai.** Bootstrap lấy mẫu lại **31 cụm SA3**; số 20 là số hành lang có ≥3 postcode ở RQ2/RQ4. Nhóm "Cao" theo E2 nằm trong 9 cụm (6 có ≥3 postcode); theo E4: 16 cụm (5 có ≥3). Lỗi này lan sang `EDA_IMPROVEMENT_VERIFICATION.md` mục 8 (do phiên khác trích lại); đã sửa ở đó.
- **Mất cân bằng nền.** Bản trước đánh giá là "Hở"; sau khi kiểm tra trên cấu hình hiện tại (E4, giai đoạn BP0019) tôi hạ xuống "Khá" và rút lại kết luận nặng: T1 vẫn vững khi kiểm soát nền và dương ở cả ba tầng giá.
- **"Nhà không hồi".** Ở các tài liệu trước tôi mô tả placebo là "nhà không hồi (−0.1)". Chính xác hơn: "nhà hồi ít hơn nhiều" (E2 ≈ 0; E4 +3.1 [+0.1; +5.2]), như phiên sửa đã đính chính.
- **Slide 5 của `PRESENTATION_AND_DECISIONS.md`** vẫn dùng số của cấu hình cũ (xem `EDA_IMPROVEMENT_VERIFICATION.md` phần E). Thông điệp 3 (hành lang) và 4 (mùa vụ) nên viết lại theo B2-B3.

## 6. Giới hạn của bản đánh giá này

- Mức Chặt/Khá/Hở/Yếu là **phán đoán của tôi**. Các phép kiểm [V] dùng bootstrap và hoán vị 1,000-2,000 lần; cận sát 0 không ổn định.
- Phép hoán vị ở RQ4 phá tương quan không gian, nên "70%/71%" là mức tham chiếu chứ không phải p-value; trong dữ liệu thật tương quan không gian có thể làm tỷ lệ vượt do ngẫu nhiên *cao hơn*.
- Tương phản căn hộ trừ nhà dùng các postcode có đủ ≥30 hợp đồng cả hai phân khúc (n=110-113 trên 117), nên mẫu hơi nhỏ hơn mẫu chính.
- Tôi **không chạy lại** notebook, và **không sửa** notebook; đánh giá dựa trên code, output đã lưu và các kiểm tra riêng. `v7_argument_checks.py` chạy trên cấu hình cũ (giai đoạn visa-cấp); `v8_current_notebook_checks.py` chạy trên cấu hình hiện tại.
