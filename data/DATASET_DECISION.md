# Quyết định sử dụng dữ liệu: chọn lọc theo bài toán của City of Sydney

*Ngày 26/10/2026. Cách hiểu: "hai data" là **GTFS** (đính kèm) và **bảng giá phòng sinh viên** (hai nguồn được nhắc cùng nhau trong tài liệu trước của bạn). Nếu bạn muốn nói hai nguồn khác, cho tôi biết.*

## 1. Kết luận ngắn

- **GTFS: không đưa vào phân tích chính.** Kết quả gần như trùng với thước đo khoảng cách hiện có và không đổi kết luận nào.
- **Giá phòng sinh viên: không đưa vào bảng phân tích.** Chỉ nên dùng như một bảng minh họa nhỏ nếu cần cho câu chuyện với Hội đồng.
- Nên chọn **gói cân bằng gồm 8 nguồn** (bên dưới). Gói này giải quyết đúng các điểm yếu đã nêu mà không ghép thừa.

## 2. Kiểm tra GTFS

| Nội dung | Kết quả |
|---|---|
| Là gì | Lịch trình tĩnh toàn Greater Sydney: 10,236 tuyến, 211,464 chuyến, 171,265 điểm dừng, 5.66 triệu dòng giờ dừng (tổng khoảng 3 GB, riêng shapes 1 GB) |
| Thời điểm | Lịch **hiện tại**, có hiệu lực từ 26/10/2026 |
| Đã thử | Với mỗi postcode (247), tìm chuyến **trực tiếp** giờ cao điểm sáng (7-9h, thứ Tư 04/11/2026) đến 16 campus lớn, đi bộ tối đa 800 m ở đầu đi và 600 m ở đầu đến |
| Độ phủ | 168 trên 247 postcode (68%) có chuyến trực tiếp tới ít nhất một campus lớn; 90% trong nhóm so sánh |
| Có bổ sung gì không | **Rất ít.** Tương quan hạng với số sinh viên đại học trên 100 dân (Census): giao thông 0.70, so với 0.77 của thước đo hiện có. Sau khi loại phần đã giải thích bởi thước đo hiện có, phần còn lại chỉ 0.18 |
| Có đổi kết luận không | **Không.** Chia nhóm theo giao thông trùng 74% với cách chia hiện có (tương quan 0.84). Chênh lệch giữa nhóm Cao và Thấp gần như không đổi (ví dụ studio/1BR: −8.9 so với −10.4 điểm trong năm đóng cửa; +8.1 so với +8.8 khi phục hồi) |
| Có giải quyết điểm bỏ sót không | **Không.** Burwood và Strathfield (nhiều sinh viên, exposure thấp) vẫn thấp |

**Vì sao không nên đưa vào:**
1. Lịch hiện tại không phản ánh mạng lưới năm 2018-2024, trong khi dữ liệu thuê trải 2018-2026.
2. Chỉ tính chuyến trực tiếp, bỏ qua đổi tuyến.
3. Nặng nề (3 GB) cho một kết quả trùng với thước đo đã có.
4. Câu hỏi về sinh viên chọn nơi ở dựa trên giao thông là câu hỏi khác, không phải câu hỏi của dự án này.

**Khi nào nên dùng lại:** nếu sau này muốn làm công cụ giúp sinh viên chọn nơi ở, hoặc đánh giá khu xa campus nhưng kết nối tốt.

## 3. Kiểm tra giá phòng sinh viên

| Nội dung | Kết quả |
|---|---|
| USyd 2026 (PDF 2 trang) | Có giá phòng mỗi tuần theo loại phòng và độ dài hợp đồng: khoảng $306 đến $603 (phòng đơn $374-$475; studio $453-$603) |
| UNSW so sánh chỗ ở | Trang tải được nhưng **không có giá trong nội dung tĩnh** (nội dung nạp động) |
| Đơn vị vận hành tư nhân | Chưa có (thường chỉ công bố giá trên website, cần thu thập tay) |

**Một so sánh minh họa** (cùng postcode quanh USyd, hợp đồng thuê mới tháng 1-9/2026): trung vị studio/1BR tư nhân $650-$885 mỗi tuần cho cả căn; trung vị 2 phòng ngủ $880-$1,200, tức khoảng $440-$600 mỗi người nếu hai người ở chung. Giá phòng USyd (khoảng $374-$475 cho phòng đơn trong căn 2 phòng ngủ khoảng $417-$465) thấp hơn hoặc tương đương. **Giới hạn:** khác đơn vị (mỗi người so với cả căn), chỉ một nhà cung cấp, một năm, giá công bố chưa phải giá giao dịch, và giả định hai người ở chung là của tôi.

**Quyết định:** không ghép vào dữ liệu phân tích. Nếu muốn, giữ một bảng nhỏ trong brief, và chỉ nêu khi kèm các giới hạn trên.

## 4. Đóng góp của từng nguồn

| Nguồn | Giải quyết điểm yếu nào | Thêm tín hiệu mới | Thay đổi kết luận | Công sức |
|---|---|---|---|---|
| **Hợp đồng thuê (lõi)** | Thước đo chính | | | Đã xong |
| **CRICOS + Bộ Giáo dục (SA4) + ABS (lõi)** | Cách đo mức gắn với trường | | | Đã xong |
| **DCJ Rent tables 2018-2022** | **Thiếu 2019-2020**, thiếu kiểm tra trước COVID | Có (xu hướng trước COVID) | Có: hai nhóm đi song song trước COVID (−0.3 và −0.2 điểm) | Thấp (một bảng) |
| **Census 2021 (theo postcode)** | **Kiểm chứng** thước đo, bỏ sót Burwood/Strathfield | Có (thước đo thứ hai: sinh viên đang sống) | Có: "giảm sâu rồi hồi mạnh" lặp lại; chênh lệch tích lũy **không vững** | Thấp-trung bình |
| **BP0019 (số visa sinh viên có mặt)** | **Giai đoạn** dựa trên visa cấp bị lệch pha | Có (mùa vụ có mặt, đỉnh 03/2025) | Có: khu gần campus không yếu đi khi số sinh viên giảm | Thấp |
| **City of Sydney Housing Audit** | Chưa có chuỗi nguồn cung chỗ ở sinh viên | Có (6,797 phòng năm 2015 lên 12,924 năm 2025) | Không (bối cảnh) | Thấp |
| Hoàn bond (refunds) | Thiếu tín hiệu về thời gian thuê | Có (ngắn hơn ở khu gần campus: 397 so với 488 ngày) | Không | Trung bình (tệp lớn) |
| Hồ sơ xin xây (DA) | Nguồn cung đề xuất | | Không | Trung bình (kéo qua API) |
| Airbnb | Thuê ngắn và trung hạn | | Không | Thấp |
| **GTFS** | Khả năng tiếp cận | Gần như không | **Không** | Cao |
| **Giá phòng sinh viên** | Khả năng chi trả | Một điểm dữ liệu | Không | Trung bình (thu tay) |

## 5. Ba gói đề xuất

| Gói | Nguồn | Phù hợp khi |
|---|---|---|
| **Gọn** | Lõi (4) + DCJ | Muốn tối thiểu, chỉ sửa điểm yếu 2019-2020 |
| **Cân bằng (khuyến nghị)** | Gọn + Census + BP0019 + Housing Audit (**8 nguồn**) | Muốn trả lời đủ bốn điểm yếu chính (trước COVID, thước đo, giai đoạn, nguồn cung) mà không ghép thừa |
| Đầy đủ | Cân bằng + hoàn bond + DA + Airbnb + giá phòng + GTFS | Không khuyến nghị: thêm công sức nhưng không đổi kết luận |

**Vì sao chọn gói cân bằng:** mỗi nguồn trong đó đổi một điều cụ thể về cách đọc kết quả (có hoặc không song song trước COVID; thước đo có khớp nơi sinh viên sống; giai đoạn có đúng; Hội đồng thực sự đã thêm bao nhiêu phòng). Các nguồn còn lại chỉ thêm bối cảnh hoặc trùng với cái đã có.

**Hai điều nên cân nhắc cắt trong phần hiện có:** Airbnb và DA trong notebook không đổi kết luận nào; có thể giữ ngắn gọn hoặc bỏ để giảm số nguồn phải giải thích.

## 6. Giới hạn của các kiểm tra này
- Là phép thử khám phá, chưa qua quy tắc xếp hạng A/B/C.
- GTFS: chỉ một ngày thứ Tư, chỉ chuyến trực tiếp, điểm đến lấy theo tâm postcode của campus (sai số khoảng 1 km).
- Giá phòng: một nhà cung cấp, một năm, khác đơn vị so với dữ liệu thuê.
- Hoàn bond, Census, ACTEID: đã nêu trong `DATA_ENRICHMENT_ASSESSMENT.md`.
