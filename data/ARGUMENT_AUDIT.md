# Đánh giá mức độ hoàn thiện về lập luận của notebook EDA chính

**Vai trò đánh giá:** senior data analyst, tập trung vào *chuỗi suy luận* chứ không phải cú pháp: mỗi section có (a) mục đích trong pipeline, (b) phương pháp EDA dùng, (c) phát hiện/khẳng định, (d) khẳng định đó **có được bằng chứng ở chính section đó đỡ không**.
**Đối tượng:** `notebooks/sydney_student_rent_eda` (số mục theo notebook). **[R]** = đọc từ code/output đã lưu; **[V]** = tôi tính lại bằng `data/verification/v7_argument_checks.py` (chạy lại được).

**Thang đánh giá lập luận**

| Mức | Nghĩa |
|---|---|
| **Chặt** | Khẳng định được bằng chứng đỡ trực tiếp; giả định được nêu và kiểm |
| **Khá** | Đúng hướng, nhưng có một giả định chưa kiểm hoặc một chi tiết chưa nêu |
| **Hở** | Có bước nhảy: con số hoặc cách diễn đạt mạnh hơn bằng chứng |
| **Yếu** | Phép thử không có khả năng phân biệt, hoặc không tạo ra kết quả |

---

## 0. Kết luận tổng

**Mức hoàn thiện lập luận: khá chặt, khoảng 7/10.**

- **Điểm làm tốt nhất:** *kết luận cuối được hiệu chỉnh đúng với bằng chứng* ("hạng B", "không tách được sinh viên khỏi cú sốc chung", "không dùng để xếp hạng hành lang"). Kết luận cuối bền **vì** nó khiêm tốn.
- **Điểm yếu:** các **phát biểu trung gian** trong từng section mạnh hơn bằng chứng, và chuỗi suy luận chính có **4 mắt xích chưa được bảo vệ** (xem mục 2). Hai kết quả phụ (mùa vụ và danh sách hành lang RQ4) **không đứng vững** khi kiểm tra.
- **Vì sao điểm không cao hơn:** dự án chưa liệt kê các *giả thuyết cạnh tranh* kèm *dự đoán khác biệt* của từng giả thuyết, nên phần "không tách được" là kết luận *mặc định* chứ chưa phải kết luận *được kiểm bằng placebo/đối chứng*.

---

## 1. Phân tích từng section: pipeline → phương pháp EDA → phát hiện → độ chặt lập luận

### Phần mở đầu: câu hỏi, phạm vi, quy tắc xếp hạng bằng chứng

| | |
|---|---|
| **Vai trò trong pipeline** | Bước 1 (đặt câu hỏi và luật chơi) |
| **Phương pháp** | 4 RQ; quy tắc A/B/C **đặt trước khi xem kết quả** |
| **Khẳng định** | "Hạng bằng chứng quyết định ngôn từ khuyến nghị" |
| **Mức** | **Chặt** về cấu trúc; **Hở** ở hai chi tiết quy tắc |
| **Lỗ hổng** | (1) Chỉ số *đồng thuận giữa các định nghĩa exposure* lấy trung bình cả cửa sổ không có tín hiệu (ρ≈0, dấu là nhiễu): theo BP0019 hạng B chỉ vừa đủ ngưỡng 60%. (2) Hạng chỉ xét T1-T3, loại T0 là cửa sổ có hiệu ứng lớn nhất, nên hạng B thực chất dựa vào **một** cửa sổ (T1). (3) Giả thuyết còn ngầm: chưa nêu "dự đoán dấu gì, kết quả nào bác bỏ" |

### §2.1-§2.3 Hiểu dữ liệu và chất lượng

| | |
|---|---|
| **Vai trò** | Bước 2-3 (hiểu và kiểm tra dữ liệu) |
| **Phương pháp** | `info/describe`, thiếu, mã lạ, trùng, khối lượng theo tháng (SQL), thứ trong tuần, IQR so với giới hạn cứng |
| **Phát hiện** | Có file trùng giữa năm và tháng; thiếu 1.5%/2.6%; trùng 6.0% (giữ); IQR gắn cờ quá nhiều nên chỉ dùng giới hạn cứng |
| **Mức** | **Chặt** |
| **Kiểm chứng [V]** | Khẳng định "file năm và tháng chứa gần như cùng các dòng" **đúng ở mức dòng**, không chỉ ở mức đếm: năm 2024, chỉ 18 dòng mỗi phía khác nhau trên 328,183 (0.005%); năm 2022: 9 và 16 dòng |
| **Lỗ hổng** | Câu "mostly plausible rents" cho các dòng IQR gắn cờ **được nêu mà không được trình bày** (không in hồ sơ các dòng bị loại); chưa phân tích mẫu thiếu (dồn vào mã `U`: 37% thiếu tiền thuê); đoạn thứ trong tuần không phục vụ kết luận nào |

### §3.1-§3.2 Làm sạch và bảng phân tích

| | |
|---|---|
| **Vai trò** | Bước 3 |
| **Phương pháp** | Quy tắc làm sạch bằng SQL, nhật ký đếm từng bước, `assert` bảng = nhật ký |
| **Phát hiện** | 2,215,281 → 2,129,444 → 1,484,734 dòng |
| **Mức** | **Khá** |
| **Lỗ hổng** | Hai giới hạn cứng ($100-$5,000; 0-8 phòng) được **đặt**, không được biện minh bằng dữ liệu (tuy ảnh hưởng nhỏ: 3,272 dòng). Phân khúc `f01` gộp studio với 1PN; giả định "nhu cầu sinh viên mạnh nhất ở căn hộ nhỏ" được nêu nhưng không kiểm (căn 2PN ở chung là nhà ở sinh viên điển hình). File 2018 cơ cấu mã khác các năm sau (mã `U` 7.3% so với 3.6%) |

### §3.3 Co giãn đặc trưng

| | |
|---|---|
| **Vai trò** | Bước 3 |
| **Phương pháp** | min-max và z-score trên 6 biến thể exposure |
| **Phát hiện** | "Các biến thể tương quan mạnh" |
| **Mức** | **Yếu** |
| **Lỗ hổng** | **Phép thử không có khả năng thay đổi kết quả:** heatmap dùng Spearman (bất biến với co giãn đơn điệu); `zscore` không được gọi. Phát hiện "tương quan mạnh" đúng nhưng không cần phép co giãn nào để thấy |

### §3.4 Dựng thước đo exposure (E1/E2/E3)

| | |
|---|---|
| **Vai trò** | Bước 3, **mắt xích trung tâm** của cả phân tích |
| **Phương pháp** | Campus = địa điểm CRICOS bậc đại học; chia ghi danh SA4 về campus theo số khóa học; suy giảm theo khoảng cách (3 mức λ) |
| **Mức** | **Khá** |
| **Điểm tốt** | Thành thật gọi đây là *giả định phân bổ*, nêu độ phân giải ~1 km, thử 6 biến thể |
| **Lỗ hổng** | (1) **Giả định thời gian không đổi** chưa được nêu: ghi danh 2025 dùng để giải thích thay đổi 2018-2021. (2) Đo *nơi học*, không phải *nơi ở* của người thuê. (3) Các biến thể cùng gốc (tương quan ~0.99), nên robustness ở §6.4 và §8 **không kiểm giả định gốc**; thước đo Census độc lập mới làm được (tương quan chỉ 0.50 trong nhóm so sánh) |

### §3.5 Chọn nhóm so sánh

| | |
|---|---|
| **Vai trò** | Bước 3 → nền cho RQ3 |
| **Phương pháp** | Nhóm đối chứng = postcode ≥35% căn hộ và ≥200 hợp đồng; chia tertile theo E2; "so sánh thay đổi, không so mức" |
| **Mức** | **Hở** |
| **Lỗ hổng [V]** | **Các nhóm không cân bằng lúc đầu:** giá nền 2018 của căn hộ nhỏ nhóm Cao $530 so với Thấp $410; tỷ lệ căn hộ 0.76 so với 0.62; tương quan hạng giữa E2 và giá nền **0.62**. Lập luận "so thay đổi nên không cần cân bằng mức" chỉ đúng nếu tốc độ tăng không phụ thuộc mức giá, nhưng tương quan hạng giữa giá nền và thay đổi T1 là **+0.29**. Thêm nữa, **13/39 postcode nhóm Cao là chính City of Sydney** (một phần ba) |
| **Kiểm tra mức độ** | Tương quan hạng E2-T1 **+0.55 → +0.50** sau khi kiểm soát hạng giá nền và tỷ lệ căn hộ: *quan hệ sống sót*. Nhưng chia theo tầng giá nền, chênh lệch T1 (nửa trên − nửa dưới của E2) là **+7.0 (n=47, rẻ), −0.2 (n=33, trung bình), +2.7 (n=37, đắt)**: *hiệu ứng không đồng đều*, dồn vào tầng giá rẻ. Notebook §9.3 tự hiển thị sự mất cân bằng nhưng không dùng nó |

### §3.6 Định nghĩa giai đoạn

| | |
|---|---|
| **Vai trò** | Bước 3 → định nghĩa các cửa sổ T0-T3 |
| **Phương pháp** | Cắt giai đoạn theo đỉnh/đáy của tổng 12 tháng visa cấp NSW |
| **Mức** | **Khá** |
| **Lỗ hổng** | Giai đoạn dài ngắn khác nhau (11, 20, 11 và 27 tháng); trung vị trong giai đoạn trộn xu hướng nội bộ (tác giả có nêu ở phần giới hạn). "Đóng cửa 2021" chỉ là phần đuôi: dữ liệu DCJ cho thấy khoảng cách mở từ **Q2/2020**, nên T0 (2018 so với 2021) kéo dài hơn cú sốc. Visa cấp là dòng chảy, lệch pha với sinh viên có mặt (đã nêu) |

### §4.1-§4.3 RQ1: chuyện gì đã xảy ra

| | |
|---|---|
| **Vai trò** | Bước 4 (mô tả) |
| **Phương pháp** | Chỉ số trung vị theo tháng (2018 = 100), bảng trung vị theo giai đoạn, kiểm tra pandas = SQL |
| **Phát hiện** | "Một chu kỳ chung chi phối; chênh lệch giữa nhóm nhỏ so với phong trào chung" |
| **Mức** | **Khá** (khẳng định *phụ thuộc thang đo*) |
| **Kiểm chứng [V]** | Đúng với **tích lũy**: 2018 → giai đoạn cuối, nhóm Cao +31.0% và nhóm Thấp +31.6% (log, trung vị gộp). **Nhưng với từng nhịp thì khác biệt không nhỏ:** sụt 2018 → đóng cửa **−17.9% (Cao) so với −7.2% (Thấp)**, hồi đóng cửa → hồi phục **+19.7% so với +11.8%**. Câu "chênh lệch nhóm nhỏ so với chuyển động chung" chỉ đúng cho tích lũy |
| **Lỗ hổng** | RQ1 dùng trung vị **gộp theo hợp đồng**, RQ3 dùng trung vị **theo postcode rồi lấy trung vị giữa postcode**: hai ước lượng "thay đổi" khác trọng số, chưa được đối chiếu. **Rent bị làm tròn:** 80% rent là bội của $10 và 77% trung vị postcode-giai đoạn là bội của $10; một bước $10 trên mốc $450 là **2.2%**, tức lớn hơn các chênh lệch 1-3 điểm % được báo cáo (T2, T3, tích lũy) |

### §4.4 Mùa vụ

| | |
|---|---|
| **Vai trò** | Bước 4-5 (khai phá thêm, **thêm sau khi đã xem kết quả**) |
| **Phương pháp** | Log trung vị tháng trừ trung bình trượt căn giữa 12 tháng; trung bình theo tháng lịch; so Cao với Thấp |
| **Phát hiện** | Tháng 2: Cao +4.1% so với Thấp +0.4%; dương ở 4/5 năm (căn nhỏ) |
| **Mức** | **Hở** |
| **Kiểm chứng [V]** | Chênh lệch **thu hẹp mạnh khi tách xu hướng theo từng postcode** thay vì gộp: **+3.6 → +1.4 điểm %** (căn nhỏ) và **+3.3 → +1.6** (chỉ 1PN). Tức hơn một nửa "tín hiệu" đến từ cách gộp nhiều postcode vào một chuỗi trung vị (hiệu ứng cơ cấu: postcode nào hoạt động tháng nào). Mức còn lại (~1.5 điểm %) **nhỏ hơn một bước làm tròn $10 (2.2%)**. Cơ cấu studio so với 1PN **không** là nguyên nhân (1PN-only gần như không đổi) |
| **Lỗ hổng** | "4/5 năm dương" có xác suất **19%** (6/32) xảy ra nếu không có hiệu ứng, và một trong năm đó là −0.1. Tác giả đã gắn nhãn "gợi ý, không phải kết luận"; nhưng *con số tiêu đề* cần được thay bằng ước lượng theo postcode |

### §5.1-§5.4 RQ2: ở đâu

| | |
|---|---|
| **Vai trò** | Bước 4 (mô tả không gian) |
| **Phương pháp** | Thay đổi log theo postcode với ngưỡng ≥30 hợp đồng ở cả hai giai đoạn; bản đồ; trung vị theo hành lang SA3 (≥3 postcode) |
| **Phát hiện** | Tăng giá lan rộng: 20 hành lang, từ +21% (Leichhardt) đến +37% (Auburn); Sydney Inner City +27%, hạng 15/20 |
| **Mức** | **Khá** |
| **Lỗ hổng** | Kết luận "lan rộng" được đỡ tốt. Nhưng **dữ kiện thú vị nhất không được diễn giải:** nội thành tăng **ít hơn** phần lớn hành lang khác (hạng 15/20), tức chính là câu chuyện "sụt sâu, hồi chưa bù hết" của RQ3, nên RQ2 và RQ3 đang nói *cùng một điều* mà văn bản không nối. Bộ lọc ≥3 postcode, ≥30 hợp đồng loại các postcode mỏng ở 2018 (chọn lọc chưa được thảo luận) |

### §6.0-§6.2 RQ3: liên hệ với exposure (so Cao − Thấp, bootstrap, Spearman)

| | |
|---|---|
| **Vai trò** | Bước 5 (suy luận thống kê, **lõi của dự án**) |
| **Phương pháp** | Chênh lệch trung vị theo nhóm; cluster bootstrap theo SA3 (2,000 lần, khoảng 90%); Spearman; hoán vị (chỉ tham khảo) |
| **Phát hiện** | T0 −10.4 [−13.9; −5.5]; **T1 +8.8 [+5.1; +11.1]**; T2, T3 ≈ 0; tích lũy −2.7 [−7.3; −0.2] |
| **Mức** | **Khá chặt** về phương pháp; **Hở** ở độ rộng khoảng tin cậy |
| **Điểm tốt** | Dùng cluster bootstrap thay vì bootstrap postcode; gắn nhãn hoán vị là lạc quan; báo cáo cả T2, T3 không có tín hiệu |
| **Lỗ hổng [V]** | (1) **Số cụm mang nhóm "Cao" rất ít:** bootstrap lấy mẫu lại 31 cụm SA3 nhưng nhóm Cao chỉ nằm trong 9 cụm, trong đó **Sydney Inner City chứa 14/39 postcode**, thực chất ~6 cụm có ý nghĩa; bootstrap với vài cụm "được điều trị" thường cho khoảng **quá hẹp**. (2) ~10 cửa sổ kiểm ở mức 90% nên kỳ vọng ~1 kết quả "có ý nghĩa" ngẫu nhiên; kết quả sát biên (tích lũy, cận trên −0.2) không đáng tin. (3) Chỉ T1 đủ mạnh, và T1 là cửa sổ "hồi sau cú sốc": **đúng thứ mà cả giả thuyết sinh viên lẫn giả thuyết cú sốc chung của nội thành đều dự đoán** |

### §6.3 So căn hộ nhỏ với căn 2 phòng ngủ

| | |
|---|---|
| **Vai trò** | Bước 5 (thử tính đặc thù của tín hiệu) |
| **Phương pháp** | Chênh lệch (gap f01) − (gap f2) giữa các nhóm |
| **Phát hiện** | Khác biệt có ý nghĩa ở 1/3 cửa sổ |
| **Mức** | **Yếu** |
| **Lỗ hổng** | **Giả định của phép thử** ("nếu sinh viên quan trọng, căn nhỏ phải mạnh hơn 2PN") **không chắc đúng:** 2PN ở chung là loại nhà sinh viên thuê điển hình (chính `DATASET_DECISION.md` giả định hai người ở chung). Hơn nữa, theo thước đo Census, 2PN cho T1 **+8.2 [+4.5; +11.3]**, gần bằng căn nhỏ (+8.7): kết quả của phép thử phụ thuộc thước đo exposure. Vì phương hướng dự đoán không rõ, kết quả nào cũng diễn giải được |

### §6.4-§6.5 Độ bền và xếp hạng

| | |
|---|---|
| **Vai trò** | Bước 5 (kiểm chứng) → ra hạng B |
| **Phương pháp** | 60 đặc tả (6 biến thể × 2 phân khúc × 5 cửa sổ); bỏ từng hành lang; áp quy tắc A/B/C |
| **Phát hiện** | Hạng **B** (1/3 cửa sổ; đồng thuận 80%; bỏ-một-hành-lang 100%) |
| **Mức** | **Khá** |
| **Lỗ hổng** | (1) Sáu biến thể **cùng gốc** nên "80% đồng thuận" gần như tautology (xem §3.4). (2) Chỉ số đồng thuận gồm cả cửa sổ ρ≈0 (đã nêu). (3) "Bỏ-một-hành-lang 100%" chỉ kiểm *dấu*, và mọi hành lang trong nhóm Cao đều là nội thành/đông, nên không kiểm được điều quan trọng nhất: *đây có phải hiệu ứng của "khu nội thành" nói chung không*. Hạng B vì vậy **đúng nhưng nên được đọc là "có hiệu ứng khu vực", chưa phải "có hiệu ứng sinh viên"** |

### §7 RQ4: hành lang nào đáng xem tiếp

| | |
|---|---|
| **Vai trò** | Bước 5-6 (ưu tiên hóa) |
| **Phương pháp** | So trung vị hành lang với trung vị nhóm Thấp trong 6 phép (2 phân khúc × T1-T3); "nhất quán" = trên chuẩn ≥5/6 và ≥2,000 hợp đồng |
| **Phát hiện** | Không hành lang gần campus nào vượt đều; hai hành lang vượt đều (Merrylands-Guildford, Ryde-Hunters Hill) đều xa campus |
| **Mức** | **Yếu** |
| **Kiểm chứng [V]** | **Quy tắc không có khả năng phân biệt.** Khi hoán vị ngẫu nhiên nhãn hành lang giữa các postcode, trung bình **1.6 hành lang** vượt ngưỡng ≥5/6; thực tế quan sát được **2**; xác suất ngẫu nhiên cho ≥2 là **48%**. Hai hành lang "vượt đều" vì vậy là mức *kỳ vọng ngẫu nhiên*, và "không hành lang gần campus nào vượt" cũng không mang thông tin (kỳ vọng 0.5 trên 6 hành lang, xác suất thấy 0 khá cao). Lý do cấu trúc: T2, T3 là hai cửa sổ không có tín hiệu, nhưng quy tắc đòi vượt chuẩn ở 5/6 phép trong đó |
| **Hàm ý** | Câu "tăng giá nhanh không đặc trưng cho khu quanh trường" **vẫn đúng**, nhưng được đỡ bởi RQ1, RQ2 và kết quả tích lũy, **không phải bởi RQ4**. Danh sách tên hành lang không nên xuất hiện trong thông điệp. Lưu ý thêm: hoán vị ngẫu nhiên phá tương quan không gian, nên tỷ lệ vượt "do ngẫu nhiên" trong dữ liệu thật có thể còn cao hơn |

### §8 Robustness

| | |
|---|---|
| **Vai trò** | Bước 5 (kiểm chứng) |
| **Phương pháp** | Ngưỡng 30/60/100 hợp đồng; bỏ City of Sydney; nhóm tứ phân vị |
| **Phát hiện** | Kết quả không đổi |
| **Mức** | **Khá** |
| **Lỗ hổng** | Cả ba kiểm tra đổi **tham số**, không đổi **giả định**: cùng E2, cùng giai đoạn, cùng ước lượng. Thiếu ba loại kiểm tra giả định: (i) **placebo** nhà 3-4 phòng ngủ (dữ liệu đã có), (ii) **xu hướng trước COVID** (DCJ), (iii) **thước đo exposure độc lập** (Census). Tác giả nêu đúng giới hạn này ở cuối §8 |

### §9.1-§9.3 Bối cảnh: DA, Airbnb, cấu trúc nền

| | |
|---|---|
| **Vai trò** | Bước 5-6 ("còn giải thích nào khác?") |
| **Phương pháp** | Đếm DA theo năm (10 tháng lấy mẫu), đếm tin Airbnb (1 thời điểm), bảng cấu trúc nền theo nhóm |
| **Phát hiện** | Không gradient rõ theo nhóm; nhóm Cao/Thấp khác nhau ở nền |
| **Mức** | **Hở** (về chức năng lập luận) |
| **Lỗ hổng** | Mục "giải thích khác" nhưng **không có liên kết suy luận** với kết quả (tác giả tự nêu "không điều chỉnh kết quả ở trên"), nên không loại được giải thích nào. DA là đề xuất (22% đề xuất 0 căn), Airbnb một thời điểm. **§9.3 phơi bày đúng vấn đề của §3.5** (nền không cân bằng) nhưng không rút hệ quả. Nên chuyển thành "những gì chưa kiểm được" |

### §10 Kết luận, khuyến nghị, giới hạn

| | |
|---|---|
| **Vai trò** | Bước 6 (truyền đạt) |
| **Phương pháp** | Văn bản sinh tự động theo hạng bằng chứng |
| **Mức** | **Khá chặt** |
| **Điểm tốt** | Khuyến nghị đổi theo hạng; nêu rõ "không dùng để xếp hạng hành lang"; mục giới hạn trung thực |
| **Lỗ hổng** | (1) Phát hiện số 1 ("chênh lệch nhóm nhỏ") phụ thuộc thang đo (xem §4.3). (2) Phát hiện số 4 (mùa vụ) dùng con số bị phóng đại. (3) Phát hiện số 5 (hành lang) dựa trên quy tắc không phân biệt (xem §7). (4) **Mục giới hạn thiếu 4 điều:** làm tròn $10; số cụm mang nhóm Cao; mất cân bằng nền giữa các nhóm; chưa có placebo. (5) Khuyến nghị chưa quy ra AUD/tuần và chưa nối với từng quyết định của người dùng |

---

## 2. Chuỗi suy luận chính và 4 mắt xích chưa được bảo vệ

```
Dữ liệu sạch → [L1] E2 đo "sinh viên có mặt ở khu" → [L2] nhóm Cao/Thấp so sánh được
  → [L3] cửa sổ thay đổi có ý nghĩa → T0/T1 có chênh lệch → [L4] chênh lệch là của "sinh viên"
```

| Mắt xích | Hiện trạng | Bằng chứng |
|---|---|---|
| **L1: E2 đo sinh viên** | Nêu là giả định, chưa kiểm bằng nguồn độc lập trong notebook chính | E2 và Census chỉ tương quan 0.50 trong nhóm so sánh; 49% postcode đổi nhóm |
| **L2: nhóm so sánh được** | "So thay đổi không so mức" chưa đủ | Nền $530 so với $410; tỷ lệ căn hộ 0.76 so với 0.62; 1/3 nhóm Cao là City of Sydney; hiệu ứng dồn vào tầng giá rẻ (+7.0, −0.2, +2.7) |
| **L3: cửa sổ có nghĩa** | Phụ thuộc cắt giai đoạn và làm tròn rent | Cắt theo BP0015 làm "tích lũy" mất ý nghĩa khi đổi sang BP0019; bước làm tròn $10 = 2.2% |
| **L4: là của sinh viên** | Chưa có phép thử phân biệt | Placebo nhà 3-4PN: nhịp sụt cũng có (−7.6) nhưng **không hồi** (−0.1); 2PN theo Census cũng hồi |

**Nhận định:** phần kết luận "không tách được" thực chất là hệ quả của việc **L4 chưa được kiểm**, không phải bằng chứng về giới hạn của dữ liệu. Với dữ liệu đã có (nhà 3-4PN, DCJ, Census) có thể *thu hẹp* được L4 trước khi xin dữ liệu mới.

---

## 3. Việc cần làm để hoàn thiện lập luận (xếp theo mức tác động)

| # | Việc | Mắt xích | Công sức | Tác động lên kết luận |
|---|---|---|---|---|
| **A1** | **Liệt kê giả thuyết cạnh tranh** (sinh viên; làm việc từ xa/văn phòng nội thành; du lịch; tâm lý rời nội thành) kèm **dự đoán khác biệt** (loại nhà, tháng, khu CBD so với khu có campus nhưng ít văn phòng), rồi chọn phép thử theo từng dự đoán | L4 | Thấp (viết) | Biến "không tách được" thành kết luận được kiểm |
| **A2** | **Thêm placebo nhà 3-4PN** cạnh căn hộ nhỏ | L4 | Thấp | Đổi diễn giải: nhịp sụt là của cả khu, chỉ nhịp hồi đặc thù căn hộ |
| **A3** | **Cân bằng nền:** báo cáo kèm tầng giá nền (hoặc hồi quy hạng có kiểm soát giá nền, tỷ lệ căn hộ); tách City of Sydney khỏi nhóm Cao ở bảng chính | L2 | Thấp-TB | Có thể thu hẹp T1 ở tầng giá trung bình |
| **A4** | **Thay RQ4 bằng bảng mô tả** hoặc thêm hiệu chỉnh bằng hoán vị (đưa ngưỡng "vượt đều" về mức ngẫu nhiên); bỏ tên hành lang khỏi thông điệp | §7 | Thấp | Loại một kết luận không có thông tin |
| **A5** | **Báo cáo mùa vụ theo ước lượng từng postcode** (+1.4 điểm %), nêu rõ nhỏ hơn bước làm tròn | §4.4 | Thấp | Hạ cấp từ "gợi ý" xuống "chưa phân biệt được" |
| **A6** | **Khoảng tin cậy cho tình huống ít cụm mang nhóm Cao:** bootstrap có cân nhắc, hoặc báo cáo kèm "~6 cụm hiệu dụng"; ghi cảnh báo đa so sánh | §6 | Thấp-TB | Khoảng rộng hơn; chỉ T0, T1 còn đứng |
| **A7** | **Thống nhất ước lượng "thay đổi"** giữa RQ1 (gộp hợp đồng) và RQ3 (trung vị postcode); thêm cảnh báo làm tròn $10 | §4-§6 | Thấp | Nhất quán; hạ độ tin cậy các chênh lệch 1-3 điểm % |
| **A8** | **Sửa quy tắc xếp hạng:** đồng thuận chỉ tính ở cửa sổ có tín hiệu; hạng = hạng thấp hơn của hai thước đo (E2 và Census); không dùng T0 làm "phát hiện" riêng nếu chưa qua placebo | §6.5 | Thấp | Hạng B thành hạng có nghĩa hơn |
| **A9** | **Viết lại phát hiện #1** theo thang: "tích lũy giống nhau (+31% so với +32%), nhưng nhịp sụt gấp ~2.5 lần ở nhóm Cao" | §4.3, §10 | Thấp | Chính xác hơn |
| **A10** | **Bổ sung 4 điều vào mục giới hạn:** làm tròn $10; số cụm mang nhóm Cao; nền không cân bằng; chưa placebo | §10 | Thấp | Trung thực hơn |
| **A11** | Chuyển §9 thành "những gì chưa kiểm được"; dùng §9.3 để biện minh cho A3 | §9 | Thấp | Đúng chức năng |

**Thứ tự:** A1-A2 trước (rẻ nhất, tác động lớn nhất lên L4), sau đó A3-A5, rồi A6-A11 khi chỉnh văn bản.

---

## 4. Điều chỉnh các nhận định trước đó của tôi (để bản ghi chính xác)

- Ở các tài liệu trước, tôi viết bootstrap dùng "~20 cụm". **Sai:** bootstrap lấy mẫu lại **31 cụm SA3**; con số 20 là số hành lang có ≥3 postcode trong bảng RQ2/RQ4. Điểm đúng là nhóm "Cao" chỉ do **9 cụm** mang (thực chất ~6). Đã sửa trong `PRESENTATION_AND_DECISIONS.md`.
- Hai phát hiện của đánh giá này **mới** so với `PRESENTATION_AND_DECISIONS.md`, nơi Slide 5 vẫn dùng chúng: (i) thông điệp 3 (hành lang) dựa vào RQ4, vốn không phân biệt được với ngẫu nhiên; (ii) thông điệp 4 (mùa vụ) dùng con số +4.1% so với +0.4% của cách gộp, trong khi ước lượng theo postcode chỉ còn chênh lệch ~1.4 điểm %. Nếu bạn đồng ý với A4 và A5, hai thông điệp này nên được viết lại: thông điệp 3 dựa trên RQ1, RQ2 và kết quả tích lũy; thông điệp 4 hạ xuống "chưa phân biệt được".

## 5. Giới hạn của bản đánh giá này

- Mức Chặt/Khá/Hở/Yếu là **phán đoán của tôi**; các kiểm tra [V] là phép thử độc lập nhưng cũng dùng bootstrap/hoán vị với 1,000 lần lặp nên các cận sát 0 không ổn định.
- Phép hoán vị ở §7 giữ nguyên tương quan trong từng postcode nhưng phá tương quan không gian; kết quả "48%" là mức tham chiếu, không phải p-value chính thức.
- Phép kiểm tra phân tầng giá nền ở §3.5 dùng chia đôi E2 *trong từng tầng* (không phải tertile của notebook), nên không so thẳng được với +8.8; nó chỉ cho thấy *tính không đồng đều*.
- Tôi **không chạy lại** toàn bộ notebook và **không thay đổi** notebook; đánh giá dựa trên code, output đã lưu, và các kiểm tra riêng.
