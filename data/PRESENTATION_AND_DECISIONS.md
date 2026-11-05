# Thuyết trình cho Business team & CEO, và thẩm định 6 quyết định trước khi sửa notebook chính

> **Cập nhật 05/11/2026:** 6 quyết định ở Phần B đã được áp dụng vào notebook chính. Vì giai đoạn chính giờ theo số sinh viên có mặt (BP0019), một số con số ở Phần A đã đổi (ví dụ T1 +8.8 thành +10.0): xem `EDA_IMPROVEMENT_VERIFICATION.md`, Phần E, trước khi dùng kịch bản này.

**Dự án:** Tiền thuê nhà mới ở Sydney có phản ứng khác nhau quanh các khu campus không?
**Phạm vi tài liệu:** (A) kịch bản thuyết trình ~15 phút bằng ngôn ngữ business; (B) thẩm định 6 quyết định ở mục 13 của `notebooks/00_data_extraction_overview`; (C) nhật ký bằng chứng.

**Quy ước nguồn của từng con số**

| Ký hiệu | Nghĩa |
|---|---|
| **[R]** | Lấy từ repo (notebook đã chạy, `PROJECT_BRIEF.md`, `DATA_ENRICHMENT_ASSESSMENT.md`...). Tôi đã đối chiếu với output đã lưu trong `.ipynb`. |
| **[V]** | Tôi tự tính lại từ `data/processed/` bằng các script trong `data/verification/` (đường dẫn tương đối, chạy lại được). |
| **[E]** | Kiến thức ngoài repo, **chưa được kiểm chứng trong dự án**; cần xác minh trước khi nói với CEO. |

---

# PHẦN A. KỊCH BẢN THUYẾT TRÌNH

## Slide 0. Kết luận trước (30 giây đầu)

> Chúng tôi dùng 2,1 triệu hợp đồng thuê mới ở NSW để hỏi: **tiền thuê quanh các trường đại học có diễn biến khác với khu tương tự nhưng xa trường không?**
>
> **Câu trả lời ngắn:** có một khác biệt, nhưng chỉ là *một nhịp sụt sâu rồi hồi mạnh* quanh thời kỳ biên giới đóng cửa. Sau đó hai nhóm khu đã đi cùng nhau. **Chưa có bằng chứng cho thấy khu gần trường tăng giá nhanh hơn một cách bền vững**, và dữ liệu hiện có **không tách được "do sinh viên" khỏi "do cú sốc chung của nội thành"**.
>
> **Độ tin cậy: hạng B (tạm thời).** Chúng tôi biết rõ cần xin thêm dữ liệu gì để nâng lên.

*Ghi chú cho người trình bày:* nói kết luận "chưa phân biệt được" như một kết quả hữu ích (nó ngăn Hội đồng phát biểu quá đà), không phải như thất bại.

---

## Slide 1. Topic và mục tiêu

| | |
|---|---|
| **Topic** | Hợp đồng thuê mới ở Greater Sydney: khu gần campus có diễn biến giá khác khu xa campus không, ở loại căn nào, lúc nào, và đáng tin đến đâu. |
| **Vì sao bây giờ** | Hội đồng City of Sydney nhất trí thông qua nghị quyết về thiếu nhà ở sinh viên giá rẻ (20/02/2023). Chính sách liên bang 2026 gắn tăng chỉ tiêu tuyển sinh quốc tế của đại học công với việc cung cấp chỗ ở. **[R]** |
| **Khoảng trống** | Hội đồng đang nói về nhà ở sinh viên bằng **số phòng và câu chuyện**; chưa có thước đo nào về việc tiền thuê quanh campus có khác biệt hay không. **[R]** |
| **Người dùng** | Chuyên viên quy hoạch/chính sách nhà ở của City of Sydney (nhóm Housing for All). **Chưa được xác nhận với người thật** (xem Slide 7). |
| **3 quyết định hỗ trợ** | (1) Hành lang nào đáng đào sâu; (2) nên phát biểu chắc đến mức nào trong báo cáo/thư vận động; (3) cần xin thêm dữ liệu gì. |
| **Không trả lời** | Sinh viên gây ra bao nhiêu % tăng giá; cắt X sinh viên thì giá giảm Y; cần xây bao nhiêu giường. |
| **4 câu hỏi** | Chuyện gì đã xảy ra? Ở đâu? Có liên hệ với campus không? Khu nào cần xem tiếp? |

Đây là phân tích **khám phá, mô tả**: không dự báo, không kết luận nhân quả.

---

## Slide 2. Dataset chứa thông tin gì

**Ba lớp dữ liệu, mỗi lớp trả lời một câu hỏi business:**

| Câu hỏi | Dữ liệu | Quy mô | Vai trò |
|---|---|---|---|
| **"Giá thuê mới là bao nhiêu?"** (kết quả cần đo) | NSW Fair Trading, tiền đặt cọc (bond) của từng hợp đồng thuê mới: ngày, postcode, loại nhà, số phòng ngủ, tiền thuê/tuần | 62 file; 2.215 triệu dòng thô, **2.129 triệu dòng hợp lệ** toàn NSW, **1.485 triệu dòng** ở 247 postcode Greater Sydney. Phủ 2018 và 01/2021-09/2026 **[R]** | Thước đo chính |
| **"Khu nào gần hoạt động giáo dục quốc tế?"** | CRICOS (danh bạ trường/khóa/địa điểm); Bộ Giáo dục (ghi danh theo vùng, 2025); ABS (ranh giới và bảng quy đổi postcode) | 485 địa điểm đại học ở Greater Sydney, 16 campus lớn; riêng nội thành Sydney chiếm ~60% ghi danh **[R]** | Dựng thước đo "mức gắn với campus" (exposure) |
| **"Khi nào sinh viên vào nhiều/ít?"** | Home Affairs: visa cấp (BP0015, *dòng chảy*) và số người giữ visa sinh viên đang có mặt (BP0019, *tồn kho*) | BP0019: 60 snapshot quý, 2011-2026 **[R]** | Chia thời gian thành các giai đoạn |

**Dữ liệu bổ sung (giai đoạn "enrichment") và dữ liệu bối cảnh:**

| Nguồn | Giải quyết điểm yếu nào | Vai trò hiện tại |
|---|---|---|
| DCJ Rent Tables 2018-2022 | Thiếu 2019-2020 | Kiểm tra xu hướng trước COVID |
| Census 2021 theo postcode | Thước đo campus chưa được kiểm chứng | Thước đo thứ hai: nơi sinh viên đại học **đang sống** |
| City of Sydney Housing Audit 2015-2025 | Chưa có chuỗi nguồn cung chỗ ở sinh viên | Biểu đồ bối cảnh (chỉ City of Sydney) |
| DA (hồ sơ xin xây), Airbnb | "Còn lý do nào khác?" | Chỉ mô tả; không đưa vào kiểm định |

**Đã cân nhắc và loại có lý do** (đây là điểm mạnh, xem Slide 6): GTFS giao thông (thử thật: kết quả trùng 74% với cách chia hiện có, không đổi kết luận), bảng giá phòng sinh viên (1 nhà cung cấp, khác đơn vị), giá bán nhà (bị chặn, giấy phép CC BY-NC-ND), tin đăng Domain/REA (điều khoản). **[R]**

**Điều dataset KHÔNG cho biết:** *ai* là người thuê (sinh viên hay không), và số sinh viên theo suburb. Mức gắn với sinh viên của từng khu được **suy ra** từ vị trí campus, không đo trực tiếp.

---

## Slide 3. Dataset có vấn đề gì, và đã xử lý thế nào

Đây là slide quan trọng nhất cho phần "chất lượng dữ liệu". Trình bày theo **rủi ro với kết luận**, không theo kỹ thuật.

### 3.1 Dữ liệu thô: "con số có sạch không?"

| Vấn đề phát hiện | Rủi ro nếu bỏ qua | Đã xử lý | Dư lượng |
|---|---|---|---|
| **Đếm đôi:** file năm và file tháng chứa cùng hợp đồng từ 2022 (tỷ lệ 1.00) | Số lượng hợp đồng và trung vị bị méo | Dùng file năm 2021 + file tháng từ 2022 | Không |
| **Thiếu giá trị:** thiếu tiền thuê 1.50%, thiếu số phòng ngủ 2.64% | Trung vị lệch | Loại, có đếm từng bước | Nhỏ |
| **Mã không hợp lệ:** loại nhà `1,3,P,G...` không có trong chú giải (65 dòng); `U` = "không rõ" theo chú giải | Phân loại sai | Loại mã lạ; giữ `U` theo chú giải | Không |
| **Giá trị bất thường:** quy tắc IQR gắn cờ **50,651** dòng, giới hạn cứng chỉ **3,272** dòng | Nếu cắt theo IQR sẽ cắt luôn các căn hộ nội thành, đúng thị trường cần nghiên cứu | **Chỉ dùng giới hạn cứng** ($100-$5,000/tuần; 0-8 phòng ngủ); IQR chỉ để kiểm tra | Không |
| **Trùng lặp:** 112,664 dòng (6.0%) giống hệt trên 5 trường, không có mã bond | Không phân biệt được "trùng" và "hai căn giống nhau trong cùng tòa nhà" | **Giữ lại** (xóa sẽ làm lệch số đếm). **[V]** tôi thử xóa: kết luận không đổi (T1: +8.8 thành +8.0 điểm %) | Không |

**Kết quả:** 2,215,281 dòng thô, giữ **2,129,444 (96.1%)**, trong đó **1,484,734** nằm trong nhóm phân tích. **[R]**
**Kiểm soát chéo:** số dòng của bảng phân tích bằng đúng nhật ký làm sạch (assert); trung vị tính bằng pandas và bằng SQL trùng nhau trên 3,613 ô; 15/15 điểm kiểm tra nguồn khớp. **[R]**

### 3.2 Khoảng trống và độ tin cậy của nguồn

| Vấn đề | Rủi ro | Đã xử lý | Dư lượng |
|---|---|---|---|
| **Thiếu 2019-2020**; 2018 lấy từ bản sao UAT của cổng dữ liệu NSW | Không kiểm tra được hai nhóm khu có đi song song *trước* COVID; nguồn 2018 chưa xác nhận | Bổ sung DCJ (tổng hợp theo quý) lấp 2019-2020. **[V]** File 2018 **khớp** số trung vị chính thức của DCJ (tương quan 0.996) nên rủi ro về *nội dung* giảm nhiều. (Lưu ý: DCJ và Fair Trading cùng xuất phát từ các bond, nên đây là kiểm tra *nhất quán*, không phải xác nhận độc lập) | Vẫn cần xác nhận nguồn UAT về mặt pháp lý/xuất xứ; DCJ chỉ là trung vị, không tính lại được |

### 3.3 Ghép dữ liệu và địa lý

| Vấn đề | Rủi ro | Đã xử lý | Dư lượng |
|---|---|---|---|
| Chỉ có **postcode**, khoảng cách đo từ tâm postcode (~1 km) | Sai số vị trí | Ghi rõ; so sánh ở cấp postcode và hành lang (SA3) | Giữ nguyên |
| UNSW (2052) và Macquarie (2109) **không có trong bản đồ ABS** | Mất hai campus lớn | Quy về postcode lân cận 2033 và 2113 | Giữ nguyên |
| **Central Coast** (10 postcode) nằm trong "Greater Sydney" của ABS nhưng là thị trường riêng | So sánh sai thị trường | Loại; còn **247** postcode | Không |
| CRICOS không có postcode | Không đặt được campus lên bản đồ | Ghép qua bảng địa điểm với kiểm tra `m:1`; khớp **100%**; loại khóa hết hạn | Không |
| Nhãn không thống nhất (sector của Bộ Giáo dục); ô "<5" bị ẩn | Gộp sai nhóm | Chuẩn hóa chữ; ô ẩn thành giá trị thiếu | Nhỏ |

### 3.4 Cái cần đo không quan sát được trực tiếp (vấn đề lớn nhất)

| Vấn đề | Rủi ro | Đã xử lý | Dư lượng |
|---|---|---|---|
| Không biết người thuê là ai; "mức gắn với campus" là **mô hình** (ghi danh theo vùng, chỉ 1 năm, tính theo *nơi học*, chia về campus theo số khóa học) | Nếu thước đo sai, mọi kết luận sai theo | 6 biến thể thước đo (giảm theo khoảng cách ở 3 mức, chia đều, khoảng cách, tỷ trọng vùng), chuẩn hóa min-max/z-score để so sánh | Cả 6 biến thể đều xuất phát từ *cùng danh sách campus* (tương quan ~0.99) nên **không** kiểm tra giả định gốc. Đây là lý do cần Census |

### 3.5 So sánh có công bằng không?

| Vấn đề | Đã xử lý |
|---|---|
| Khu gần campus **vốn đắt hơn và nhiều căn hộ** hơn | So sánh **mức thay đổi**, không so mức giá; mốc 2018 |
| Nội thành toàn căn hộ nhỏ, không so được với khu nhà riêng | Nhóm đối chứng chỉ gồm postcode có ≥35% căn hộ và ≥200 hợp đồng căn hộ nhỏ/2PN năm 2018 (104 postcode đối chứng + 13 postcode City of Sydney) |
| Tiền thuê lệch phải | Dùng thay đổi log (phần trăm đối xứng) |
| Ô quá mỏng cho trung vị | Tối thiểu 30 hợp đồng/ô ở cả hai giai đoạn; thử lại ở 60 và 100 (kết quả không đổi) |
| Các postcode lân cận có chung điều kiện | Khoảng bất định tính bằng **cluster bootstrap** (lấy mẫu lại cả hành lang), không bootstrap từng postcode |
| Giai đoạn dựa trên *visa cấp* (dòng chảy), lệch pha với *sinh viên có mặt* | Bổ sung BP0019 (xem Quyết định 1) |

### 3.6 Đối chiếu với kỹ năng wrangling trong tài liệu học (Day 2-4)

| Nội dung tài liệu | Dự án đã làm | Nhận xét |
|---|---|---|
| Day 2: head/tail, info, null, duplicates, đổi tên cột, filter, range, outlier, categorical, boxplot | Đủ cả: `head/tail/info`, tỷ lệ thiếu, đếm trùng, đổi tên cột (DoE, 2018), `describe` có phân vị, mã loại nhà, boxplot theo loại nhà | Đạt, và **có lý giải** vì sao giữ trùng, vì sao không cắt IQR |
| Day 3: data quality issues, IQR, feature scaling, function | Bảng tóm tắt vấn đề (mục 2.3), so IQR với giới hạn cứng, min-max/z-score/log, hàm tái dùng (`iqr_bounds`, `minmax`, `zscore`, `profile`) | Đạt |
| Day 4: grouping, merge, time series | `groupby` theo postcode × phân khúc × giai đoạn; merge nhiều nguồn có `validate`; chỉ số theo tháng, trung bình trượt, tách xu hướng để tìm mùa vụ | Đạt |
| *Vượt chương trình* | DuckDB SQL đối chiếu pandas, GeoPandas (bản đồ, `sjoin`), bootstrap, quy tắc xếp hạng bằng chứng đặt trước | Điểm cộng |

---

## Slide 4. Cách chúng tôi giữ kết luận trung thực

Trước khi xem kết quả, mỗi mối liên hệ được xếp hạng **A / B / C**:

| Hạng | Quy tắc (rút gọn) | Cách nói trong báo cáo |
|---|---|---|
| **A** | Khoảng 90% không chứa 0 ở ≥2 trong 3 giai đoạn sau đóng cửa; ≥80% cách đo khác cùng dấu; bỏ từng hành lang dấu vẫn giữ ≥90% | "Mối liên hệ ổn định, đáng đào sâu" |
| **B** | ≥1 giai đoạn không chứa 0 và ≥60% cách đo đồng ý | "Tín hiệu tạm thời, phụ thuộc cách đo" |
| **C** | Còn lại | "Chưa phân biệt được với xu hướng chung" |

Kết quả hiện tại: **hạng B.** Không hạng nào hàm ý nhân quả. **[R]**

---

## Slide 5. Kết quả: bốn thông điệp

**1. Một chu kỳ chung chi phối tất cả.** Căn hộ nhỏ ở City of Sydney: **$570 (2018) → $480 (2021, −16%) → $775 (+36% so với 2018)**; khu xa campus cũng +37%. Căn 2 phòng ngủ: $780 → $650 → $1,100 (+41%), khu xa campus +38%. **[R]** Tăng giá lan rộng ở cả 20 hành lang, không riêng khu quanh trường.

**2. Khác biệt duy nhất là một nhịp "sụt sâu rồi hồi mạnh".** So nhóm khu gần campus với nhóm xa (căn hộ nhỏ): sụt sâu hơn **10.4 điểm %** khi đóng cửa, hồi mạnh hơn **8.8 điểm %** khi mở lại, sau đó chênh lệch **≈ 0** (+0.9 và −0.8). **[R]**
Dữ liệu DCJ cho thấy rõ hơn theo quý (căn 1PN): khoảng cách mở ra từ **Q2/2020** (−6.3), sâu nhất **Q4/2020** (−13.8), và **khép lại hoàn toàn vào Q4/2022** (−0.5). **[V]**
→ Với CEO: "Khu gần trường từng bị giảm giá mạnh hơn và đã bù lại; hiện hai nhóm đang đi cùng nhau."

**3. Không có hành lang nào gần campus luôn vượt mức tham chiếu.** 0 trong 6 hành lang có mức gắn campus cao vượt chuẩn ở ≥5/6 phép so sánh; hai hành lang vượt đều (Merrylands-Guildford, Ryde-Hunters Hill) đều là khu *xa* campus. → Tăng giá nhanh **không đặc trưng** cho khu quanh trường. **[R]**

**4. Một gợi ý mùa vụ, chưa phải kết luận.** Căn hộ nhỏ ở khu gần campus cao hơn xu hướng +4.1% vào tháng 2, khu xa chỉ +0.4%; chênh lệch tháng 2-3 dương ở 4/5 năm. Chỉ có 5 chu kỳ và phân tích này được thêm sau khi đã thấy kết quả đầu. → Là *giả thuyết để kiểm tra* bằng dữ liệu ngày bắt đầu hợp đồng từ nhà cung cấp chỗ ở sinh viên. **[R]**

**Hai thông tin bổ trợ từ dữ liệu bổ sung** **[R]**: (i) khi chia giai đoạn theo số sinh viên có mặt, giai đoạn số sinh viên giảm có chênh lệch ≈ 0, tức chưa thấy khu gần campus yếu đi; (ii) thời gian giữ bond ở khu gần campus ngắn hơn (397 so với 488 ngày, căn 1PN), nhất quán với luân chuyển nhanh hơn nhưng cũng có thể do cư dân trẻ ở căn nhỏ, và số liệu bị cắt cụt về phía ngắn.

---

## Slide 6. Điểm mạnh của dự án

| # | Điểm mạnh | Bằng chứng |
|---|---|---|
| 1 | **Bài toán gắn với một quyết định thật**, có người dùng và tài liệu gốc | Nghị quyết 20/02/2023; chính sách liên bang 2026 |
| 2 | **Làm sạch có kế toán đầy đủ**: mọi dòng bị loại đều được đếm, và có kiểm tra chéo tự động | 2.215M → 2.129M; assert; pandas = SQL trên 3,613 ô |
| 3 | **Xử lý có lý giải, không máy móc** (giữ trùng, không cắt IQR, loại Central Coast) | Mục 2.1 và 3.1 của notebook; **[V]** xóa trùng không đổi kết luận |
| 4 | **Chọn so sánh công bằng**: so *thay đổi* chứ không so mức, nhóm đối chứng cùng cấu trúc nhà | Mục 3.5 |
| 5 | **Quy tắc xếp hạng bằng chứng đặt trước** và ngôn từ khuyến nghị tự đổi theo hạng | Mục "Evidence grading" |
| 6 | **Khoảng bất định đúng kiểu** (bootstrap theo cụm hành lang) và có nhiều lớp kiểm tra độ bền | Mục 6.4, 8 |
| 7 | **Đối chiếu nhiều nguồn độc lập**: DCJ khớp bond (0.997); Census kiểm chứng thước đo campus (0.77) | `DATA_ENRICHMENT_ASSESSMENT.md` |
| 8 | **Ghi lại cả những gì *không* đưa vào và vì sao** (GTFS đã thử thật rồi loại) | `DATASET_DECISION.md` |
| 9 | **Trung thực về giới hạn**: khẳng định "chưa phân biệt được" thay vì nói quá | Mục 10.3 |
| 10 | **Tái lập được** theo chuỗi script đánh số + README | `scripts/01-06`, `DATA_README.md` |

---

## Slide 7. Vùng cần hoàn thiện (xếp theo mức ảnh hưởng đến kết luận)

| # | Vấn đề | Bằng chứng | Hướng xử lý |
|---|---|---|---|
| **1** | **Chưa tách được "sinh viên" khỏi "cú sốc chung của nội thành"**; chưa chạy kiểm định placebo dù dữ liệu đã có | **[V]** Nhà 3-4 phòng ngủ ở nhóm "Cao" cũng sụt **−7.6 điểm %** (căn hộ nhỏ: −10.4) nhưng **không hồi** (T1: −0.1, so với +8.8 của căn hộ nhỏ). Nghĩa là *nhịp sụt là hiện tượng của cả khu*, chỉ nhịp hồi là đặc trưng của căn hộ | Thêm placebo vào notebook; sửa lời diễn giải |
| **2** | **Kết quả "tích lũy từ 2018" (−2.7 điểm %) mong manh** | Khoảng 90% chỉ vừa chạm −0.2; **đổi dấu** (+1.1, khoảng chứa 0) khi dùng thước đo Census; mất ý nghĩa khi dùng giai đoạn theo số có mặt; nhà 3-4PN còn lệch −7.3, tức đây là hiện tượng chung của khu đắt (tăng phần trăm chậm hơn) | Không coi là phát hiện; bỏ khỏi thông điệp chính |
| **3** | **Thước đo "mức gắn campus" là mô hình**; các biến thể cùng gốc | Tương quan ~0.99 giữa 6 biến thể; Census chỉ khớp 0.50 trong nhóm so sánh | Thêm Census làm thước đo thứ hai (Quyết định 3) |
| **4** | **Khoảng bất định có thể hẹp hơn thực tế**: bootstrap lấy mẫu lại 31 cụm SA3, nhưng nhóm "Cao" chỉ do 9 cụm mang (14/39 postcode nằm trong một cụm, Sydney Inner City; thực chất ~6 cụm có ý nghĩa); kiểm định ~10 cửa sổ ở mức 90% | **[V]** Các kết quả sát biên đổi khi nhiễu nhỏ: ví dụ T3 chuyển thành "có ý nghĩa" (−4.0 đến −0.1) khi xóa trùng; T2 theo Census có cận dưới 0.1 | Chỉ coi hiệu ứng *lớn* (T0, T1) là phát hiện; ghi rõ cảnh báo đa so sánh |
| **5** | **Thiếu 2019-2020 ở mức từng hợp đồng**; DCJ chỉ là trung vị theo quý | **[V]** "Song song trước COVID" nhạy với định nghĩa: chênh lệch 2018→2019 của căn 1PN là −0.4 (trung vị năm) đến −2.1 (trung bình năm); độ dốc trước COVID −1.24 điểm %/năm (khoảng 90%: −3.08 đến −0.06) | Phát biểu "gần song song (trong ~2 điểm %/năm)", không phải "song song" (Quyết định 2) |
| **6** | **Giai đoạn dựa trên visa cấp** | Đỉnh visa cấp 07/2023, đỉnh sinh viên có mặt 03/2025: lệch ~20 tháng | Quyết định 1 |
| **7** | **Persona chưa được xác nhận** với người thật | `PROJECT_BRIEF.md` mục 4, điểm 12 | Một buổi phỏng vấn 30 phút với chuyên viên City of Sydney |
| **8** | **Khả năng tái lập chưa trọn vẹn** | **[V]** 4 script (`08_parse_dcj_rent`, `08a_...`, `09_...`, `10_...`) hard-code `/Users/chipi/...`; **không có script nào** sinh bảng chênh lệch DCJ (số trong tài liệu chỉ tái lập được khi dùng "trung vị theo năm") | Dùng đường dẫn tương đối; commit script DCJ |
| **9** | **Một số tài liệu đã cũ** so với kết quả mới | `PROPOSAL_v2.md` vẫn nói "chưa có kết quả mô hình"; `PROJECT_BRIEF.md` còn nêu −2.7 như phát hiện sơ bộ | Cập nhật sau khi chạy lại notebook |
| **10** | **Giai đoạn "đóng cửa 2021" gộp hai cú sốc** | **[E]** Greater Sydney có phong tỏa nội địa cuối 06/2021 đến giữa 10/2021, trùng với giai đoạn này và với đêm Census (08/2021). Cần xác minh ngày chính xác trước khi dùng | Nêu trong phần giới hạn |

---

## Slide 8. Khuyến nghị và đề nghị với lãnh đạo

**Khuyến nghị cho Hội đồng (theo hạng B):**
1. Dùng kết quả như **bối cảnh mô tả** ("giá thuê căn hộ hồi phục mạnh sau 2021 ở mọi khu"), **không** dùng để xếp hạng khu cho hành động liên quan đến sinh viên.
2. Khi viết báo cáo/thư vận động, dùng ngôn từ "tín hiệu tạm thời, chưa phân biệt được với xu hướng chung của nội thành".
3. Theo dõi giai đoạn số sinh viên giảm: hiện chưa thấy khu gần campus yếu đi.

**Đề nghị (ask) với business team và CEO:**

| Đề nghị | Vì sao | Nâng được điều gì |
|---|---|---|
| Xin nhà cung cấp chỗ ở sinh viên/trường: **ngày bắt đầu hợp đồng và địa chỉ học kỳ theo suburb** | Là cách duy nhất kiểm tra gợi ý mùa vụ và đo sinh viên theo khu | Có thể tăng độ chắc chắn của kết luận (chưa chắc đủ để lên hạng A) |
| Xin **tỷ lệ lấp đầy và giá phòng** của nhà ở sinh viên chuyên dụng | Hiện chỉ có số phòng, không có mức sử dụng | Khả năng chi trả |
| Xin **bond 2019-2020 ở mức từng hợp đồng** | DCJ chỉ là trung vị | Kiểm tra xu hướng trước COVID chặt hơn |
| **30 phút phỏng vấn** một chuyên viên City of Sydney | Persona chưa xác nhận | Đảm bảo sản phẩm đúng nhu cầu |

---

## Slide 9. Câu hỏi dự kiến từ CEO

| Câu hỏi | Trả lời ngắn (có bằng chứng) |
|---|---|
| **"Vậy sinh viên có làm tăng giá thuê không?"** | Dự án không trả lời câu này và không được thiết kế để trả lời. Chúng tôi đo xem khu gần trường có khác khu xa trường không: khác biệt chỉ tạm thời quanh 2020-2022 và nay đã khép lại. |
| **"Sao không chỉ ra khu cần ưu tiên?"** | Vì không hành lang nào gần campus *nhất quán* vượt mức tham chiếu. Xếp hạng bây giờ là nói quá bằng chứng. |
| **"Số sinh viên đang giảm, giá thuê quanh trường có giảm không?"** | Chưa thấy (chênh lệch ≈ 0). Nhưng mới ~15 tháng, số sinh viên có mặt giảm 8-13% so với cùng kỳ năm trước, và là số liệu cả nước. **[V]** |
| **"Dữ liệu có đáng tin không?"** | Giữ 96% dòng; khớp số liệu chính thức của DCJ (tương quan 0.997); mọi dòng bị loại đều được đếm. Điểm yếu thật: thiếu 2019-2020 và không biết ai là người thuê. |
| **"Sao không dùng Airbnb, giao thông, giá bán?"** | Đã thử hoặc cân nhắc: giao thông không đổi kết luận (trùng 74%); Airbnb chỉ có một thời điểm; giá bán bị chặn và vướng giấy phép. |
| **"Cần gì để chắc hơn?"** | Slide 8: dữ liệu địa chỉ học kỳ và ngày bắt đầu hợp đồng, tỷ lệ lấp đầy, bond 2019-2020. |
| **"Chi phí hồi phục cú sốc COVID khác gì sinh viên?"** | Chưa tách được: nhà riêng cùng khu cũng sụt (−7.6) nhưng không hồi, còn căn hộ nhỏ thì hồi. Đây chính là điều cần dữ liệu tốt hơn. |

---
---

# PHẦN B. THẨM ĐỊNH 6 QUYẾT ĐỊNH (mục 13 của `00_data_extraction_overview`)

## B.0 Bảng tổng hợp

| # | Quyết định | Kết luận | Mức chắc chắn |
|---|---|---|---|
| **1** | Giai đoạn theo BP0019 hay giữ cả hai? | **BP0019 làm chính; giữ giai đoạn theo visa cấp như một dòng độ nhạy duy nhất, không chạy song song hai bản.** | Cao về hướng chọn. Kết luận chính không đổi, nhưng hạng B theo BP0019 chỉ vừa đủ ngưỡng (xem B.1) |
| **2** | Dùng DCJ "1 Bedroom" và "2 Bedrooms" cho 2018-2022? | **Có, với 4 điều kiện** (xem dưới). Bedsitter *không* phải vấn đề lớn. | Cao |
| **3** | Thêm Census làm thước đo exposure thứ hai? | **Có, báo cáo song song, và khóa quy tắc kết hợp trước khi chạy lại** (hạng = hạng yếu hơn). | Cao |
| **4** | Chỉ giữ G01, G02, G15, G37? | **Giữ 4 bảng; không thêm G33, G40.** | Cao |
| **5** | Housing Audit chỉ làm biểu đồ bối cảnh City of Sydney? | **Đồng ý**, kèm 3 ràng buộc về cách trình bày. | Rất cao |
| **6** | Bỏ BP0015, DA, Airbnb? | **DA và Airbnb: bỏ (giữ 2 dòng trong giới hạn). BP0015: chỉ bỏ được *nếu* Quyết định 1 chọn BP0019**, và khi đó phải giữ mốc ngày của nó như độ nhạy. | Cao |

### Quan hệ phụ thuộc giữa các quyết định (không được quyết riêng lẻ)

```
Quyết định 1 (giai đoạn) ──► Quyết định 6 (số phận BP0015)
Quyết định 3 (Census)    ──► Quyết định 4 (lấy bảng Census nào)
Quyết định 1 + 3         ──► Quy tắc xếp hạng (phải khóa TRƯỚC khi chạy lại)
Quyết định 2, 5          ──  độc lập
```

Lý do cần nói rõ: câu hỏi 6 nêu "bỏ BP0015 vì không đổi kết luận nào". **Điều đó đúng với DA và Airbnb nhưng không đúng với BP0015**: nó định nghĩa 5 giai đoạn mà *mọi* con số trong RQ1-RQ4 dựa vào. Chỉ khi Quyết định 1 thay giai đoạn, và chứng minh được kết luận không đổi (bằng chứng ở dưới), thì mới bỏ được.

---

## B.1 Quyết định 1: Giai đoạn theo số sinh viên có mặt (BP0019) hay visa cấp (BP0015)?

**Kết luận: dùng BP0019 làm chính; giữ giai đoạn cũ như một dòng độ nhạy.**

**Bằng chứng [V]** (chạy lại `scripts/09` với đường dẫn sửa; nhóm Cao − Thấp theo E2, căn hộ nhỏ, điểm %, khoảng 90% theo cụm hành lang):

| Cửa sổ | Giai đoạn theo **visa cấp** (hiện tại) | Giai đoạn theo **số có mặt** (BP0019) |
|---|---|---|
| T0: 2018 → đóng cửa | −10.4 [−14.0; −5.1] | −10.7 [−14.0; −5.1] |
| **T1: đóng cửa → hồi phục** | **+8.8 [+5.3; +11.1]** | **+10.0 [+7.1; +12.9]** |
| T2 | +0.9 [−2.4; +3.8] | −3.7 [−5.5; +2.2] |
| T3 | −0.8 [−2.7; +0.1] | −0.0 [−1.0; +2.0] |
| Tích lũy từ 2018 | −2.7 [−7.2; **−0.2**] | −2.7 [−6.7; **+0.6**] |

**Lập luận:**
1. **Cửa sổ duy nhất mang thông tin (T1) gần như giống nhau** vì cả hai thước đo cùng có đáy ở 11-12/2021. Cả hai cách chia đều chỉ có **1/3** cửa sổ sau đóng cửa không chứa 0, nên hạng **không thể lên A** và kết luận chính không đổi. **Nhưng hạng B theo số-có-mặt chỉ vừa đủ [V, `v5_grade_under_stock_phases.py`]:** mức đồng thuận giữa các định nghĩa exposure giảm từ **80% xuống đúng 60%** (chính là ngưỡng tối thiểu của hạng B) và độ ổn định khi bỏ từng hành lang giảm từ **100% xuống 87%**. Một ngưỡng chặt hơn một chút sẽ cho hạng C. Cách chia theo visa cấp tái lập chính xác output của notebook (1/3; 80%; 100%; B), nên phép tính lại đáng tin.
2. **Phần khác biệt nằm ở T2/T3, vốn là các cửa sổ "không có tín hiệu"**, và ở kết quả tích lũy (chuyển từ "có ý nghĩa" sang "không", xác nhận nó mong manh).
3. **Về khái niệm, "người đang có mặt" gần với nhu cầu thuê nhà hơn "visa được cấp"**: visa cấp bao gồm cấp lại cho người đã ở Úc và cấp cho người chưa đến, nên lệch pha với nhu cầu thực. Dữ liệu cho thấy lệch ~20 tháng ở đỉnh (07/2023 so với 03/2025). **[R]**
4. **Lý do quyết định:** cách chia theo visa cấp gộp "đi ngang" và "giảm" vào *một* giai đoạn 27 tháng (07/2024-09/2026). Cách chia theo số có mặt tách được giai đoạn giảm (từ 07/2025), tức là trả lời được câu hỏi chính sách "khi số sinh viên giảm, khu gần campus có yếu đi không?". Cách chia cũ không trả lời được.

**Điều kiện và cảnh báo:**
- BP0019 **chỉ có cấp quốc gia**, mọi lĩnh vực (không riêng đại học, không riêng NSW); chỉ có snapshot cuối quý và **dao động mùa rất mạnh** (tháng 12: 409k-465k; tháng 3: 544k-595k). Nếu mô tả giảm, dùng *so với cùng kỳ năm trước*: 09/2026 so với 09/2025 là **−12.5%**, 03/2026 so với 03/2025 là **−8.6%**, 12/2025 so với 12/2024 là **−7.7%**. **[V]** (Con số "−17.5% từ đỉnh" trong tính toán thô trộn lẫn mùa, không nên dùng.)
- Giai đoạn giảm mới ~15 tháng, nên "chênh lệch ≈ 0" là *chưa thấy dấu hiệu*, không phải "chắc chắn không có".
- **Không chạy hai bản song song**: sẽ nhân đôi số bảng và tạo thêm "đường rẽ" để chọn kết quả đẹp.

---

## B.2 Quyết định 2: DCJ "1 Bedroom" và "2 Bedrooms" cho 2018-2022 (biết "Bedsitter" không gộp được)

**Kết luận: Có. Nhưng phải thêm 4 điều kiện, vì độ mạnh của kết luận "song song trước COVID" thấp hơn tài liệu đang nói.**

**Bằng chứng [V]:**

| Kiểm tra | Kết quả | Ý nghĩa |
|---|---|---|
| Khớp với bond tự tính (căn hộ 1-2PN, 117 postcode) | Tương quan 2018: **0.996**; 2021: **0.999**; 2022: **0.996**. Lệch ≤ $10: 91.6%, 96.0%, 85.9% | DCJ dùng được, và file 2018 (UAT) khớp số chính thức |
| "Bedsitter" quan trọng đến đâu? | Studio (0 phòng ngủ) chỉ là **2-10% của nhóm căn hộ nhỏ** (nhóm Cao: 6-10%; nhóm Thấp: 2-5%) | Mất Bedsitter làm hẹp đôi chút phạm vi, **không** làm méo kết luận |
| Độ phủ sau khi ô ≤10 hợp đồng bị ẩn | Căn 2PN: **100%** mọi nhóm. Căn 1PN: nhóm Cao 98-100%, nhóm Thấp chỉ **84-92%** trong 2018-2020 | Ô bị ẩn **lệch về nhóm Thấp** (khu ít hợp đồng) |
| Song song trước COVID (độ dốc 2018Q1-2019Q4, Cao − Thấp) | 2PN: **+0.34** điểm %/năm [−0.67; +1.02]. 1PN: **−1.24** [−3.08; −0.06] | 2PN song song; 1PN **trôi nhẹ** (gần 0 nhưng khoảng chạm sát mức 0) |
| Cùng cú sốc COVID đo bằng gì? | Khoảng cách 2019→2020: −6.5 đến −13.8 điểm % tùy định nghĩa | Chênh lệch trước COVID nhỏ hơn cú sốc từ **3 đến hơn 10 lần** |
| Độ nhạy định nghĩa (1PN, 2018→2019) | −0.4 (trung vị theo năm), −2.1 (trung bình theo năm), +0.1 (chỉ Q4) | Con số "−0.3" trong tài liệu **tái lập được chỉ với trung vị theo năm**, và không script nào trong repo sinh ra nó |

**4 điều kiện:**
1. **Phát biểu đúng mức:** "gần song song trước COVID (lệch trong khoảng 2 điểm %/năm; căn 1PN có xu hướng trôi nhẹ)", không phải "song song".
2. **Cố định định nghĩa** (trung vị theo năm hay trung bình theo năm) và **commit script** sinh bảng, vì hiện chưa có.
3. **Kiểm tra độ bền với ô bị ẩn:** chỉ giữ postcode có đủ dữ liệu ở các mốc so sánh, hoặc báo cáo cả hai.
4. **Dùng như một bảng riêng 2018-2022**, không ghép chuỗi với trung vị của bond (hai đại lượng khác bản chất: trung vị theo quý đã tổng hợp so với trung vị theo giai đoạn).

**Giá trị lớn nhất của DCJ (nên đưa lên slide):** nó **định ngày** cú sốc: khoảng cách mở từ Q2/2020, sâu nhất Q4/2020, **khép lại hẳn ở Q4/2022**. Điều này vừa củng cố tính hợp lý của so sánh vừa đổi cách kể chuyện: "một nhịp tạm thời đã khép lại".

---

## B.3 Quyết định 3: Thêm thước đo Census (sinh viên đại học trên 100 dân) và báo cáo cả hai?

**Kết luận: Có. Báo cáo song song, nhưng phải khóa trước quy tắc kết hợp để tránh chọn kết quả thuận lợi.**

**Bằng chứng [V]:**

| Nội dung | Kết quả |
|---|---|
| E2 (campus) so với E4 (Census) | Tương quan hạng **0.77** trên 247 postcode nhưng chỉ **0.50** trong nhóm so sánh 117 postcode; chỉ **49%** postcode rơi vào cùng nhóm Thấp/Giữa/Cao |
| Hai thước đo thực sự khác nhau | Nhóm "Cao" theo E4 có tiền thuê trung vị **$500** (nhóm Cao theo E2: **$575**) và thu nhập hộ thấp hơn; **10 trong 13** postcode City of Sydney nằm trong nhóm Cao của E4 |
| Burwood (2134), Strathfield (2135) | ~12 sinh viên/100 dân nhưng E2 thấp (8.6; 5.4): campus bỏ sót; E4 xếp vào "Cao" |

Kết quả nhóm Cao − Thấp, căn hộ nhỏ (giai đoạn theo visa cấp; **[V]** tái chạy `scripts/09`):

| Cửa sổ | E2 (campus) | E4 (Census) |
|---|---|---|
| T0 | −10.4 [−14.0; −5.1] | −7.8 [−12.5; −4.2] |
| **T1** | **+8.8 [+5.3; +11.1]** | **+8.7 [+4.7; +11.1]** |
| T2 | +0.9 [−2.4; +3.8] | +1.8 [**+0.1**; +4.9] |
| T3 | −0.8 [−2.7; +0.1] | −0.2 [−1.6; +1.6] |
| Tích lũy | −2.7 [−7.2; −0.2] | **+1.1** [−1.6; +3.7] |

**Lập luận:**
1. **Mô hình "sụt sâu rồi hồi mạnh" lặp lại ở một cách chia nhóm khác hẳn** (chỉ 49% postcode cùng nhóm). Đây là bằng chứng độ bền *thật*, khác với 6 biến thể E2 vốn cùng gốc.
2. **Kết quả tích lũy đổi dấu** (−2.7 sang +1.1): xác nhận nó không đáng tin; phải bỏ khỏi thông điệp chính.
3. **"Căn hộ nhỏ đặc thù hơn căn 2PN" chỉ đúng theo E2.** Theo E4, căn 2PN cho T1 = +8.2 [+4.5; +11.3], gần bằng căn hộ nhỏ (+8.7). Do đó phép so "căn nhỏ so với 2PN" **không** là bằng chứng ủng hộ giả thuyết sinh viên.
4. **E4 không phải thước đo sạch về sinh viên quốc tế:** gộp sinh viên trong nước; Census tháng 8/2021 diễn ra khi biên giới đóng; tương quan 0.54 với tỷ lệ thuê nhà (nên có thể chỉ bắt "khu nhiều người trẻ thuê nhà"). Vì vậy E4 là thước đo *bổ sung*, không thay thế E2.

**Rủi ro nếu không khóa quy tắc:** theo E4, T1 và T2 cùng "không chứa 0" (T2 chỉ vừa qua mức, cận dưới +0.1), nghĩa là quy tắc hạng A (≥2 cửa sổ) có thể bị chạm *bằng một biên 0.1 điểm %*. Nếu báo cáo "thước đo nào đẹp hơn", đó là chọn kết quả. **Phải khóa trước:**

> **Hạng cuối cùng = hạng thấp hơn trong hai thước đo (E2, E4).** Kết quả nào đổi dấu giữa hai thước đo thì ghi "không bền" và không đưa vào thông điệp.

**Việc đi kèm:** chạy một độ nhạy với biến thể `uni_ft1524_per_100` (sinh viên đại học toàn thời gian 15-24 tuổi): tương quan hạng với E4 hiện dùng chỉ **0.78**, nên việc chọn biến thể có thể đổi nhóm.

---

## B.4 Quyết định 4: Chỉ 4 bảng Census (G01, G02, G15, G37) hay lấy thêm G33 và G40?

**Kết luận: giữ 4 bảng, không lấy G33 và G40.**

**Bằng chứng [V] và [R]:**
- **G40** (tiền thuê theo loại chủ nhà) mô tả *chủ nhà*, không phải người thuê. Chiều "loại chủ nhà" **đã có sẵn trong G37** (tên bảng: "Tenure and *Landlord Type* by Dwelling Structure"). Lấy G40 là trùng lặp (hơn 100 cột).
- **G33** là thu nhập hộ theo *hộ gia đình có/không có gia đình*, không có "hộ ở ghép". Tôi thử dùng tỷ lệ hộ không có gia đình làm chỉ báo: tương quan hạng chỉ **0.35 với E4** nhưng **0.73 với tỷ lệ thuê nhà** và **0.78 với E2**. Tức nó đo "khu hộ nhỏ ở nội thành", không đo sinh viên, và không cung cấp tín hiệu sinh viên độc lập.
- Thêm bảng nghĩa là thêm thước đo thứ ba: **tăng số "đường rẽ"** trong khi vấn đề thật là độ tin cậy của thước đo, không phải thiếu bảng.
- Thứ nên làm thay thế: kiểm tra độ nhạy trên biến thể đã có sẵn trong bảng đặc trưng (`uni_ft1524_per_100`), xem Quyết định 3.

---

## B.5 Quyết định 5: Housing Audit chỉ là biểu đồ bối cảnh City of Sydney?

**Kết luận: Đồng ý.**

**Bằng chứng [V]/[R]:**
- PDF xác nhận bảng theo "village" **gộp** "boarding house rooms, co-living, student accommodation rooms, residential..." nên không tách được sinh viên theo khu, càng không theo postcode.
- Chuỗi phòng ở sinh viên đối chiếu với CSV đã trích và PDF: 6,797 (2015) → 12,924 (2025), **+90.1%** (PDF ghi đúng "up 90.1% since 2015"); cộng khớp từng năm (2015: 2,853 + 6,797 + 741 = 10,391; 2025: 3,458 + 12,924 + 764 = 17,146). Từ 2019: **+22.6%**.
- Nguồn này **không tham gia bất kỳ phép kiểm định hay xếp hạng nào**, nên đưa vào hay không đều không đổi hạng bằng chứng.

**3 ràng buộc khi trình bày:**
1. Ghi rõ "*phòng* ở sinh viên trong ranh giới City of Sydney, tính đến tháng 6 mỗi năm".
2. **Không chia cho số sinh viên Greater Sydney** (khác phạm vi địa lý và khác năm: Census 2021 ghi 122,151 người giữ visa sinh viên ở Greater Sydney), và **không đặt chồng lên đường giá thuê** (gợi ý nhân quả).
3. Nói rõ phần lớn sinh viên ở nhà thuê tư nhân (khoảng 77% theo Census 2021 toàn quốc, 5.5% ở nhà không phải hộ gia đình) để người xem hiểu vì sao dự án tập trung vào hợp đồng thuê tư nhân. **[R]**

---

## B.6 Quyết định 6: Bỏ BP0015, DA và Airbnb khỏi notebook chính?

**Kết luận: DA và Airbnb: bỏ. BP0015: chỉ bỏ nếu Quyết định 1 chọn BP0019, và vẫn giữ 2 mốc ngày như độ nhạy.**

**DA (hồ sơ xin xây) [V]/[R]:**
- Không dùng trong kiểm định hay xếp hạng. Không có gradient theo nhóm: trung vị số DA/năm City of Sydney 21.6, Cao 48.0, Giữa 31.2, Thấp 48.0; số căn đề xuất/năm 33.6 / 63.0 / 64.8 / 67.2.
- Dữ liệu yếu: chỉ 10 tháng lấy mẫu (tháng 1 và 7 mỗi năm); là *đề xuất*, không phải căn đã xây; **22% DA ở nhóm so sánh đề xuất 0 căn** (cải tạo, hàng rào...) **[V]**.

**Airbnb [R]:** một snapshot 17/09/2026, không có lịch sử, trong khi thay đổi giá trải 2021-2026, nên **không thể dùng làm biến kiểm soát**. City of Sydney có trung vị 228 tin đăng so với 70 ở nhóm Thấp, nhưng không nối được về thời gian.

**BP0015:** là nguồn *định nghĩa* các giai đoạn của mọi kết quả (RQ1-RQ4), không chỉ "bối cảnh". Có thể bỏ khỏi việc *nạp* (134,822 dòng) nếu:
- Quyết định 1 chọn BP0019, **và**
- ghi 2 mốc (đáy 11/2021, đỉnh 07/2023) thành hằng số có chú thích nguồn để giữ dòng độ nhạy. Kết quả ở B.1 là bằng chứng "đổi giai đoạn không đổi kết luận chính".

**Việc đi kèm:**
- Giữ **một slide "những gì chúng tôi không kiểm định được"** (nguồn cung và cho thuê ngắn hạn). CEO gần như chắc chắn sẽ hỏi hai câu này; câu trả lời trung thực là "đã xem, dữ liệu hiện có không đủ để kiểm định".
- Chuyển mã DA/Airbnb sang một notebook phụ lục thay vì xóa, để không mất công sức.

---

## B.7 Những điều list 6 quyết định không hỏi, nhưng ảnh hưởng đến kết luận

| # | Việc | Lý do (bằng chứng) |
|---|---|---|
| **7** | **Thêm placebo bằng nhà 3-4 phòng ngủ** vào notebook chính | Dữ liệu đã tính sẵn nhưng chưa chạy. Kết quả [V]: nhà cùng khu cũng sụt −7.6 nhưng không hồi (−0.1). Đổi cách diễn giải "nhịp sụt là của cả khu; nhịp hồi là đặc trưng của căn hộ" |
| **8** | **Hạ cấp "chênh lệch tích lũy từ 2018" khỏi danh sách phát hiện** | Mong manh theo 3 trục: thước đo (E4), giai đoạn (BP0019), và còn nhỏ hơn mức −7.3 của nhà riêng |
| **9** | **Cố định cảnh báo đa so sánh** | ~10 cửa sổ ở mức 90%, 31 cụm nhưng chỉ ~6 cụm mang nhóm "Cao": chỉ coi hiệu ứng lớn (T0, T1) là phát hiện |
| **10** | **Sửa hard-code đường dẫn và commit script DCJ** | 4 script hard-code `/Users/chipi/...`; không có script sinh bảng DCJ |
| **11** | **Sửa cách tính "mức đồng thuận giữa các định nghĩa exposure" trong quy tắc xếp hạng** | Chỉ số này lấy trung bình *cả các cửa sổ không có tín hiệu*, nơi ρ ≈ 0 và dấu chỉ là nhiễu. **[V]** Theo số-có-mặt: T1 đồng thuận 100% nhưng T2 chỉ 20% (ρ từ −0.14 đến +0.15), kéo trung bình xuống đúng 60%, sát ngưỡng B. Nên tính đồng thuận *chỉ trên các cửa sổ có tín hiệu* (T0, T1), đặt trước khi chạy lại |

## B.8 Quy tắc phải khóa trước khi sửa notebook chính (đề xuất)

1. **Giai đoạn:** chính = BP0019 (số có mặt); độ nhạy = mốc theo visa cấp (hằng số).
2. **Thước đo:** E2 và E4 báo cáo song song; **hạng = hạng thấp hơn**; kết quả đổi dấu giữa hai thước đo = "không bền".
3. **Phát hiện đủ điều kiện:** chỉ hiệu ứng có khoảng 90% không chứa 0 *và* giữ dấu ở cả hai thước đo *và* cả hai cách chia giai đoạn. (Theo dữ liệu hiện tại: chỉ T0 và T1 của căn hộ nhỏ.) Mức đồng thuận giữa các định nghĩa exposure chỉ tính trên các cửa sổ đạt điều kiện này, không tính trên cửa sổ ρ ≈ 0.
4. **Placebo:** nhà 3-4PN báo cáo ngay cạnh căn hộ nhỏ.
5. **Kết quả tích lũy:** mô tả, không xếp hạng.
6. **DCJ:** định nghĩa năm cố định (trung vị theo năm), script đi kèm, phát biểu "gần song song".

---
---

# PHẦN C. NHẬT KÝ BẰNG CHỨNG

## C.1 Những gì tôi tự tính lại

| Script (`data/verification/`) | Kiểm tra | Thời gian |
|---|---|---|
| `v1_dcj_checks.py` | Khớp DCJ với bond theo năm; tỷ lệ studio trong nhóm căn hộ nhỏ; độ phủ sau khi ô ≤10 hợp đồng bị ẩn | ~20 giây |
| `v2_pretrend.py` | Khoảng cách Cao − Thấp hằng năm (3 cách gộp năm); đường quý theo mốc 2019Q4; độ dốc trước COVID có khoảng bất định | ~40 giây |
| `v3_placebo_dedup.py` | Placebo nhà 3-4PN; độ nhạy khi xóa dòng trùng | ~60 giây |
| `v4_census_checks.py` | E2 so với E4; bảng chéo nhóm; hồ sơ nhóm; thử G33 | ~5 giây |
| `v5_grade_under_stock_phases.py` | Tính lại hạng bằng chứng (số cửa sổ không chứa 0, đồng thuận exposure, bỏ từng hành lang) theo hai cách chia giai đoạn | ~60 giây |
| `scripts/09_enrichment_prototype.py` (đường dẫn sửa trong bản sao tạm) | Giai đoạn visa-cấp so với số-có-mặt × E2 so với E4 | ~70 giây |

Chạy từ thư mục `data/verification/`: `python3 v1_dcj_checks.py` (cần `pandas`, `numpy`, `scipy`, `pyarrow`).

## C.2 Chỗ tôi tái lập được và chỗ lệch với tài liệu

| Mục | Tài liệu | Tôi tính | Kết luận |
|---|---|---|---|
| E2 so với E4, tương quan hạng (247 / nhóm so sánh) | 0.77 / 0.50 | 0.77 / 0.50 | Khớp |
| Khoảng cách theo giai đoạn × E2/E4 (`scripts/09`) | Như bảng trong `DATA_ENRICHMENT_ASSESSMENT.md` | Khớp (bootstrap 1,000 lần) | Khớp |
| DCJ khớp bond (2,741 ô) | 0.997; 64% trùng; 91% lệch ≤$10 | 0.997; 64%; 91% | Khớp |
| Khoảng cách DCJ 1PN, 2018→2019 | −0.3 | −0.4 (trung vị năm) / −2.1 (trung bình năm) | Tái lập được *chỉ với* trung vị theo năm; không có script trong repo |
| Khoảng cách DCJ 1PN, 2019→2020 | −9.6 | −8.7 (trung vị năm) / −6.5 (trung bình năm) | Cùng hướng, độ lớn nhạy định nghĩa |
| Số sinh viên có mặt: đỉnh và hiện tại | 595,339 (03/2025) và 491,361 (09/2026) | Khớp; phần trăm giữa hai số này là −17.5% | Hai snapshot khác mùa nên không so thẳng; dùng so với cùng kỳ năm trước: −7.7% đến −12.5% |
| `da_residential`: "100% có số căn" | Notebook in "100%" | 99.8% có giá trị, nhưng 22% bằng 0 | Không mâu thuẫn, nhưng "100%" dễ gây hiểu lầm |

## C.3 Giới hạn của chính phần thẩm định này

- Mọi con số **[V]** dùng bootstrap theo cụm SA3 (31 cụm, trong đó nhóm "Cao" chỉ do ~6 cụm mang) với 1,000-2,000 lần lặp, nên các cận sát 0 (ví dụ +0.1, −0.2, −0.1) **không ổn định**; tôi không xây kết luận trên chúng.
- Tôi chỉ chạy lại các phép được yêu cầu; **chưa** chạy lại toàn bộ notebook chính sau khi đổi giai đoạn và thước đo (việc đó thuộc bước sau khi bạn trả lời 6 câu hỏi).
- Mục **[E]** (phong tỏa nội địa 2021) là kiến thức ngoài repo, cần xác minh.
- Không có phép nào ở đây là chứng minh nhân quả; kết luận "không tách được sinh viên khỏi cú sốc chung" là kết luận về giới hạn của dữ liệu, không phải bằng chứng "không có tác động".
