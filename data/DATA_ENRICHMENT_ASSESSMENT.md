# Đánh giá các nguồn dữ liệu bổ sung (data enrichment)

Ngày kiểm tra: 26/10/2026. Mỗi nguồn được mở, tải thử và parse; kết quả đo bằng dữ liệu của dự án. Các phép thử là **khám phá, chưa đưa vào notebook** và không phải kết quả đã xếp hạng.

## 1. Quyết định

**Có thể bổ sung dữ liệu để phân tích sâu hơn.** Năm nguồn nên đưa vào ngay, hai nguồn dùng có điều kiện, và một số nguồn nên hoãn. Điểm quan trọng nhất: **khoảng trống 2019-2020 có thể lấp ở dạng tổng hợp** và dữ liệu tổng hợp này khớp với dữ liệu từng hợp đồng của dự án.

| # | Nguồn | Đã xác minh | Quyết định |
|---|---|---|---|
| 1 | **NSW DCJ Rent and Sales Reports** (bảng thuê theo quý) | Có | **Đưa vào (ưu tiên 1)** |
| 2 | **ABS Census 2021 DataPacks (theo postcode)** | Có | **Đưa vào (ưu tiên 2)** |
| 3 | **BP0019: số người giữ visa sinh viên đang có mặt** | Có, chỉ cấp quốc gia | **Đưa vào** để chia lại giai đoạn và xem mùa vụ |
| 4 | **NSW Rental Bond Refunds (hoàn bond)** | Có, từng bản ghi | **Đưa vào** (nguồn mới, có tín hiệu về thời gian thuê) |
| 5 | **City of Sydney Housing Audit 2015-2025** | Có | **Đưa vào** như chuỗi nguồn cung chỗ ở sinh viên (chỉ City of Sydney) |
| 6 | **ABS ACTEID 2021** | Có, chỉ cấp vùng thủ phủ | Dùng có điều kiện, làm bối cảnh |
| 7 | NSW Housing Supply | Có | **Không đưa vào** (chỉ từ 07/2024; hoàn thành chỉ cấp bang) |
| 8 | Bảng giá phòng sinh viên (USyd, UNSW) | Chưa tải | Hoãn (trả lời câu hỏi khác) |
| 9 | GTFS giao thông | Đã biết (xem trước đây) | Hoãn |
| 10 | CPI (giá thuê điều chỉnh lạm phát) | Chưa tải | Hoãn (mất tác dụng khi so hai nhóm cùng thời điểm) |
| 11 | Inside Airbnb, thêm snapshot | Chưa tải | Hoãn (chỉ có 12 tháng gần nhất) |
| 12 | Lịch học các trường | Có xem trang | Hoãn (trang chỉ nêu 2026-2028, không có lịch sử) |

## 2. Kết quả kiểm tra từng nguồn

### 2.1 DCJ Rent and Sales Reports: lấp khoảng trống 2019-2020
- **Là gì:** bảng XLSX theo quý, **theo postcode × loại nhà × số phòng ngủ**: giá thuê phân vị 25%, trung vị, phân vị 75%, số bond mới, số bond đang giữ. Có đủ từ 03/2018 đến 03/2026 (đã tải 20 quý từ 03/2018 đến 12/2022).
- **Khớp với dữ liệu hiện có:** so với trung vị tự tính từ dữ liệu từng hợp đồng (căn hộ 1 và 2 phòng ngủ, 117 postcode) trong các quý trùng nhau (2,741 ô): tương quan **0.997**, 64% ô trùng chính xác, 91% lệch không quá $10 mỗi tuần, số bond khớp tỷ lệ 1.03.
- **Độ phủ cho 2019-2020:** có dữ liệu trong ít nhất 6 trên 8 quý ở 108 trên 117 postcode (căn 1 phòng ngủ) và 117 trên 117 postcode (căn 2 phòng ngủ).
- **Giới hạn:** là trung vị tổng hợp (không tính lại được từ từng hợp đồng); ô có 10 bond trở xuống bị ẩn; "Bedsitter" và "1 Bedroom" tách riêng nên chỉ so sánh được với nhóm 1 phòng ngủ, không gộp được với studio.
- **Phép thử:** chênh lệch giữa nhóm gần campus (Cao) và xa campus (Thấp) trong thay đổi giá theo năm:

| Căn | 2018 → 2019 | 2019 → 2020 | 2020 → 2021 | 2021 → 2022 |
|---|---|---|---|---|
| 1 phòng ngủ | **−0.3** | **−9.6** | −0.6 | +6.8 |
| 2 phòng ngủ | **−0.2** | **−5.0** | +0.2 | +2.1 |

*(điểm phần trăm, chênh lệch trung vị giữa nhóm Cao và Thấp)*. Trước COVID hai nhóm **đi song song**; khác biệt xuất hiện trong 2019-2020, tức giai đoạn biên giới đóng. Điều này củng cố tính hợp lý của việc so sánh hai nhóm, nhưng vẫn không tách được tác động của sinh viên khỏi cú sốc chung của nội thành.

### 2.2 Census 2021 (theo postcode): kiểm chứng thước đo exposure
- **Có thể tải:** gói NSW theo postcode (13 MB). Bảng G15 (loại cơ sở giáo dục đang theo học), G01, G02 (trung vị), G37 (nhà ở theo hình thức sở hữu) được đọc thành công.
- **Phép thử:** số cư dân đang học đại học trên 100 dân (Census) so với thước đo exposure từ vị trí campus (E2):
  - tương quan hạng **0.77** trên toàn bộ 247 postcode, **0.50** trong 117 postcode so sánh.
  - Các postcode có tỷ lệ sinh viên cao nhất (2008, 2050, 2007, 2033, 2032) đều có E2 cao.
  - Nhưng Burwood (2134) và Strathfield (2135) có khoảng 12 sinh viên/100 dân, trong khi E2 thấp (8.6 và 5.4), nghĩa là thước đo từ vị trí campus **bỏ sót** một số cụm sinh viên đang sống.
- **Dùng làm exposure thứ hai (E4):** chia nhóm Cao/Thấp theo số sinh viên đại học trên 100 dân. Hiện tượng "giảm sâu hơn rồi hồi mạnh hơn" **lặp lại** với E4: chênh lệch trong năm đóng cửa là −7.8 (1 phòng ngủ) và −11.2 (2 phòng ngủ) điểm, và khi phục hồi là +8.7 và +8.2 điểm, khoảng 90% đều không chứa 0. Nhưng chênh lệch **tích lũy từ 2018** đổi dấu tùy cách đo (E2: −2.7 điểm; E4: +1.1 điểm với khoảng chứa 0), nên không vững.
- **Cấu trúc nhóm:** nhóm Cao có tỷ lệ thuê nhà 70% so với 55% ở nhóm Thấp, trung vị tiền thuê Census $575 so với $460, và trung vị thu nhập hộ $2,422 so với $2,009 mỗi tuần.
- **Giới hạn:** Census tính cả sinh viên trong nước; Census tháng 8/2021 diễn ra khi biên giới đóng nên du học sinh bị thiếu; G15 không tách du học sinh.

### 2.3 BP0019: số người giữ visa sinh viên đang có mặt
- **Có thể tải và parse:** 60 snapshot hằng quý, từ 31/12/2011 đến 30/09/2026, theo loại visa, quốc tịch và loại đương đơn. **Không có chiều địa lý** (không có bang), nên chỉ dùng được cấp quốc gia.
- **Điều quan trọng:** số sinh viên (stock, đương đơn chính) và số visa cấp (flow) **lệch pha**. Số có mặt chạm đáy 268,529 (12/2021), đạt đỉnh **595,339 (03/2025)**, và còn 491,361 (09/2026). Trong khi dòng visa cấp ở NSW đạt đỉnh 07/2023.
- **Có mô hình theo mùa rõ:** số có mặt cao ở các kỳ cuối tháng 3 và tháng 9, thấp ở tháng 12 và tháng 6 (ví dụ 2024: 587k, 523k, 594k, 444k).
- **Phép thử chia lại giai đoạn theo số có mặt** (đóng cửa đến 12/2021; phục hồi 2022-2023; đi ngang 01/2024 đến 06/2025; giảm từ 07/2025): với căn 1 phòng ngủ, chênh lệch nhóm Cao so với Thấp trong giai đoạn đi ngang là −3.7 điểm (khoảng 90%: −5.5 đến 2.2) và trong giai đoạn giảm là **khoảng 0** (−0.0). Tức là chưa thấy dấu hiệu khu gần campus yếu đi so với khu xa khi số sinh viên giảm.

### 2.4 Bond Refunds (hoàn bond): thời gian thuê
- **Từng bản ghi:** ngày hoàn bond, postcode, loại nhà, phòng ngủ, số ngày bond được giữ (**Days Bond Held**), khoảng 310,000 dòng mỗi năm (kiểm tra 2023-2024, 639,027 dòng).
- **Phép thử (căn hộ 1-2 phòng ngủ):** thời gian giữ bond trung vị ở nhóm Cao ngắn hơn nhóm Thấp:

| Căn | Nhóm Thấp | Nhóm Cao | Tỷ lệ dưới 1 năm: Thấp / Cao |
|---|---|---|---|
| 1 phòng ngủ/studio | 488 ngày | 397 ngày | 33% / 41% |
| 2 phòng ngủ | 652 ngày | 554 ngày | 22% / 27% |

  Điều này nhất quán với luân chuyển nhanh hơn quanh campus, nhưng cũng có thể do cấu trúc cư dân trẻ và căn nhỏ ở nội thành.
- **Giới hạn:** các bond chưa được hoàn (hợp đồng còn tiếp diễn) không có trong tệp, nên thời gian bị lệch về phía ngắn.

### 2.5 City of Sydney Housing Audit
- **Có đủ 11 báo cáo** (06/2015 đến 06/2025). Số liệu bạn nêu được **xác nhận từ bản gốc**: 12,924 phòng ở sinh viên, tăng ròng 804 phòng trong 2024/25.
- **Chuỗi phòng ở sinh viên (cuối tháng 6):** 6,797 (2015), 7,624 (2016), 9,101 (2017), 9,352 (2018), 10,537 (2019), 10,688 (2020), 10,937 (2021), 11,529 (2022), 11,714 (2023), 12,120 (2024), 12,924 (2025).
- **Giới hạn:** chỉ City of Sydney; bảng theo "village" gộp phòng ở sinh viên với nhà trọ và chăm sóc người già nên không tách được theo khu cho riêng sinh viên.

### 2.6 ACTEID 2021
- **Datacube XLSX công khai** (283 KB). Chi tiết địa lý chỉ tới vùng thủ phủ: **Greater Sydney có 122,151 người giữ visa sinh viên** trong đêm Census 2021 (NSW: 132,633).
- **Bảng nơi ở theo loại visa (cả nước):** trong 348,556 người giữ visa sinh viên, khoảng **77% thuê nhà** (59% qua đại lý, 13% qua người không cùng hộ), khoảng **5.5% ở nhà không phải hộ gia đình** (gồm nhà ở sinh viên) và khoảng 14% ở nhà thuộc sở hữu (cả sở hữu hẳn lẫn thế chấp). Đây là số liệu **đo được** thay cho các con số mâu thuẫn trong báo cáo ngành, nhưng của năm 2021 (biên giới đóng).
- **Giới hạn:** không có postcode hay SA2; các ô được điều chỉnh ngẫu nhiên.

### 2.7 NSW Housing Supply
Bảng XLSX có sẵn nhưng chỉ từ **07/2024**; số nhà hoàn thành chỉ có ở cấp bang, theo hai loại (nhà riêng và loại khác). Không lấp được khoảng trống 2018-2026 và trùng chức năng với hồ sơ xin xây (DA) đã có.

## 3. Những gì dữ liệu mới thay đổi

| Câu hỏi | Trước | Sau khi bổ sung |
|---|---|---|
| Hai nhóm có đi song song trước COVID không? | Chưa kiểm tra được | Có: chênh lệch 2018→2019 xấp xỉ 0 |
| Thước đo "gần campus" có phản ánh nơi sinh viên sống không? | Chưa kiểm chứng | Tương quan hạng 0.77 (toàn bộ) và 0.50 (nhóm so sánh); có điểm bỏ sót (Burwood, Strathfield) |
| "Giảm sâu hơn rồi hồi mạnh hơn" có vững không? | Chỉ một cách đo | Lặp lại với thước đo độc lập (Census) |
| Chênh lệch tích lũy từ 2018 có vững không? | Có (−2.7 điểm) | **Không:** đổi dấu theo cách đo |
| Giai đoạn "điều chỉnh" có đúng không? | Dựa trên visa cấp | Số có mặt đạt đỉnh 03/2025, nên giai đoạn nên chia lại |
| Khu gần campus có yếu đi khi số sinh viên giảm? | Chưa kiểm tra | Chưa thấy (chênh lệch khoảng 0 khi chia theo số có mặt) |
| Sinh viên ở đâu? | Các nguồn mâu thuẫn | Khoảng 77% thuê nhà (Census 2021, cả nước) |
| Có tín hiệu luân chuyển cao hơn quanh campus không? | Không có | Thời gian thuê ngắn hơn ở nhóm Cao |

## 4. Rủi ro khi dùng dữ liệu bổ sung
1. Census gộp sinh viên trong nước và du học sinh, và diễn ra khi biên giới đóng.
2. DCJ là trung vị tổng hợp, không dùng được để tính lại phân vị hay gộp các nhóm.
3. BP0019 và ACTEID không có chi tiết theo postcode, nên chỉ dùng cho giai đoạn, mùa vụ và bối cảnh.
4. Thời gian giữ bond bị lệch do dữ liệu bị cắt cụt.
5. Mọi phép thử ở đây chưa đi qua quy tắc xếp hạng A/B/C và được thêm sau khi đã thấy kết quả trước, nên cần coi là khám phá.
6. Không nguồn nào cho biết **ai** là người thuê, tỷ lệ lấp đầy hay giá thực trả của nhà ở sinh viên; thông tin này vẫn phải xin từ trường hoặc đơn vị vận hành.

## 5. Kế hoạch tích hợp đề xuất
1. **Thêm mục "kiểm tra xu hướng trước COVID"** dùng DCJ (2018-2020).
2. **Thêm exposure thứ hai (E4, Census)** và báo cáo kết quả theo cả E2 lẫn E4.
3. **Chia lại giai đoạn** theo số sinh viên có mặt (BP0019) và so với cách chia hiện tại như một kiểm tra độ bền.
4. **Thêm mục thời gian thuê** từ dữ liệu hoàn bond.
5. **Thêm chuỗi phòng ở sinh viên** của City of Sydney vào phần bối cảnh.
6. Cập nhật quy tắc xếp hạng để tính cả hai thước đo exposure, rồi chạy lại notebook.

Tệp liên quan: `scripts/08a_download_enrichment_sources.py`, `08_parse_dcj_rent.py`, `09_enrichment_prototype.py`; bảng đã xử lý: `processed/dcj_rent_postcode_2018_2022.parquet`, `census2021_poa_features.csv`, `bp0019_students_by_snapshot.parquet`.
