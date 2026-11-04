# Proposal v2: Bằng chứng về rent flat quanh campus cho City of Sydney

Trạng thái: đã parse dữ liệu để kiểm tra thiết kế. **Chưa có kết quả mô hình.** Mọi con số trong mục 3 là chẩn đoán thiết kế (trung vị chưa hiệu chỉnh), không phải kết luận về tác động của du học sinh.

---

## 0. Những gì thay đổi so với PROPOSAL.md (v1)

| # | v1 nói | Kiểm tra dữ liệu cho thấy | Thay đổi |
|---|---|---|---|
| 1 | End user là chuyên viên chính sách NSW (chung chung) | Bằng chứng mạnh nhất tìm được là nghị quyết của **City of Sydney Council** (mục 1) | Persona: chuyên viên quy hoạch/nhà ở của City of Sydney |
| 2 | Giai đoạn sinh viên "tăng 2022-2024, giảm 2025-2026" | BP0015 (NSW, đương đơn chính) đạt đáy 11/2021, **đỉnh 07/2023**, giảm mạnh trong 2024, đi ngang 2025, giảm tiếp 2026 | Dùng 4 pha theo dữ liệu (mục 4.3) |
| 3 | Gradient exposure giữa các SA4 của Greater Sydney | Exposure dồn vào 1 SA4 (60%) nên gradient thực chất là "nội thành so với phần còn lại" | Làm trong nội thành, exposure ở cấp postcode, SA4 chỉ để kiểm chứng |
| 4 | Placebo là nhà 3-4 phòng ngủ | Trong City of Sydney, nhà 3-4 phòng ngủ chỉ chiếm **3.7%** bond | Placebo chuyển sang postcode đối chứng không có campus |
| 5 | Baseline là 2021 | Mọi nhóm đều giảm 10-15% ở flat năm 2021 so với 2018 (COVID) | Thêm baseline 2018; thừa nhận thiếu 2019-2020 |
| 6 | M5: "% rent mỗi 100.000 sinh viên" | Phụ thuộc quá nhiều bước quy đổi | Bỏ. Báo cáo chênh lệch giữa hai mức exposure, khoảng bất định và AUD/tuần |

---

## 1. End user và bằng chứng

**Persona:** chuyên viên quy hoạch chiến lược / chính sách nhà ở của **City of Sydney** (hỗ trợ Housing for All Working Group), và tương tự ở các council nội thành lân cận (Inner West, Randwick, Waverley).

| Bằng chứng | Nguồn | Độ tin cậy |
|---|---|---|
| Council nhất trí thông qua (20/02/2023, Item 13.3) nghị quyết "Affordable Student Accommodation Shortage": yêu cầu CEO báo cáo về các chiến lược xử lý áp lực nhà ở và chi phí sinh hoạt của sinh viên, và chuyển vấn đề sang Housing for All Working Group | [Minutes](https://meetings.cityofsydney.nsw.gov.au/documents/d4117/Printed%20decision%20Affordable%20Student%20Accommodation%20Shortage.pdf?T=5) (đã đọc toàn văn) | Cao (tài liệu gốc), nhưng là năm 2023 |
| Nghị quyết nêu: City of Sydney có khoảng 40% nhà cung cấp giáo dục của NSW; số phòng ở sinh viên tăng từ 4,223 (2012) lên 11,529 (2022) theo Housing Audit 2022; nhà ở sinh viên được báo là kín chỗ | Cùng tài liệu | Cao với tư cách trích dẫn của council, chưa kiểm chứng số liệu gốc |
| Chính sách liên bang 2026 gắn tăng phân bổ cho đại học công lập với "provision of student accommodation" | [DoE 2026 settings](https://www.education.gov.au/managed-system-international-education/2026-managed-growth-settings) (đã đọc) | Cao |
| Council dùng kênh planning proposal cho nhà ở sinh viên (ví dụ co-living ở Redfern) | [City of Sydney planning proposal](https://meetings.cityofsydney.nsw.gov.au/documents/s104783/Public%20Exhibition%20-%20Planning%20Proposal%20-%2044-78%20Rosehill%20Street%20Redfern%20-%20Sydney%20Local%20Environmental%20.pdf) (mới thấy trong kết quả tìm kiếm, chưa đọc) | Trung bình |
| Ngành cho rằng khung quy hoạch NSW thiếu điều khoản nhà ở sinh viên | Property Council (nguồn của bên có lợi ích) | Thấp đến trung bình |

**Giới hạn của bằng chứng persona:**
- Tôi chưa tìm được tài liệu 2025-2026 của City of Sydney về chủ đề này.
- Chưa phỏng vấn ai. Việc họ sẽ dùng bằng chứng từ bond là giả thuyết cần xác nhận với một người làm việc thật.
- Đây là lý do không chọn Bộ Giáo dục liên bang hay cố vấn của một đảng làm persona: dữ liệu ở độ phân giải postcode không đủ để trả lời "cắt bao nhiêu".

**Vì sao khớp với dữ liệu:** City of Sydney có 13 postcode phần lớn thuộc LGA (2000, 2007, 2008, 2009, 2010, 2011, 2015, 2016, 2017, 2018, 2037, 2043, 2050), khoảng 38,000 bond mỗi năm (2024). Các postcode này nằm trong SA4 chiếm 60% enrolment quốc tế của Greater Sydney.

---

## 2. Business problem

**Tình trạng hiện tại của end user:** bằng chứng của council chủ yếu là số phòng ở sinh viên, giá của một nhà cung cấp và tin báo chí. Chưa có thước đo nào cho thấy rent hợp đồng mới của flat gần campus có diễn biến khác với các thị trường flat tương tự nơi khác hay không.

**Phát biểu:**
> Trong từng hành lang campus ở nội thành Sydney, rent hợp đồng mới của studio/1BR và 2BR có diễn biến khác biệt, ổn định và đủ lớn so với các thị trường flat tương đương xa campus hay không, qua các pha sinh viên tăng và giảm? Từ đó council nên ưu tiên hành lang nào cho việc thu thập bằng chứng, vận động và thẩm định đề xuất nhà ở sinh viên, và có thể nói chắc đến mức nào.

**Quyết định được hỗ trợ:**
1. Hành lang nào ưu tiên đào sâu (Haymarket/CBD, Ultimo/Broadway, Redfern/Camperdown, Kensington, hay không hành lang nào).
2. Mức khẳng định phù hợp khi viết briefing hoặc thư vận động (ví dụ "có tín hiệu nhất quán", "chưa phân biệt được với xu hướng chung").
3. Cần xin thêm dữ liệu gì (số sinh viên theo suburb, tỷ lệ lấp đầy nhà ở sinh viên).

**Không giải quyết:** cần xây bao nhiêu giường; cắt bao nhiêu sinh viên thì rent giảm bao nhiêu.

---

## 3. Kết quả kiểm tra thiết kế (dữ liệu đã parse)

Tất cả là chẩn đoán. Trung vị chưa hiệu chỉnh cơ cấu, nhóm exposure do tôi định nghĩa từ file SA4.

| Phát hiện | Số liệu |
|---|---|
| Exposure SA4 dồn vào một nơi | Trong Greater Sydney: City and Inner South 60.1%, Eastern Suburbs 15.3%, Parramatta 10.4%, Ryde 4.9%; 10 SA4 còn lại mỗi nơi ≤2.2% |
| Mẫu số không đổi thứ hạng | Tương quan hạng giữa tỷ trọng enrolment và enrolment trên 100 bond/năm: 0.985 |
| Exposure đi cùng mức rent nền và cơ cấu nhà | Spearman giữa exposure và rent flat nền 2021: 0.42; City and Inner South có 42% bond là studio/1BR, các SA4 ngoại thành chỉ 3-7% (n=14 SA4, chỉ mang tính gợi ý) |
| Placebo nhà lớn không khả thi trong City of Sydney | 44.3% studio/1BR, 27.8% 2BR, 3.7% nhà 3-4 phòng ngủ |
| 2021 không phải baseline sạch | Chỉ số 2018=100, năm 2021, flat: nhóm exposure cao 85, trung bình 87, thấp 87; nhà 3-4 phòng ngủ: 97, 100, 109 |
| Sau đó các nhóm di chuyển gần nhau | Năm 2026, studio/1BR: 145 (cao), 143 (trung bình), 139 (thấp); nhà 3-4 phòng ngủ: 141, 147, 151 |
| Cỡ mẫu đủ ở cấp postcode-năm trong City of Sydney | Số bond studio/1BR năm 2024 mỗi postcode từ 393 đến 2,483 (13 postcode); cấp postcode-quý-phân khúc ở ngoại thành mỏng (trung vị 20, 34% ô dưới 10) |
| Có một khoảng trống dữ liệu | 2018 có (331,880 bond, từ bản sao UAT của data.nsw), 2019-2020 không tìm thấy; 2021 đến 2026-09 có đủ |

**Hệ quả:** chênh lệch giữa nhóm exposure cao và thấp, nếu có, nhiều khả năng nhỏ so với biến động chung của thị trường (khoảng +40% từ 2018 đến 2026 ở cả ba nhóm). Một kết quả "không phân biệt được" là khả năng thực tế và vẫn hữu ích cho persona.

### Dữ liệu aggregate: nhận xét thêm
- **BP0015 (visa granted):** đã parse pivot cache, 2,311,756 bản ghi. Có đủ chiều tháng, bang đăng ký của provider, sector, onshore/offshore, đương đơn chính/phụ. NSW, đương đơn chính, tổng 12 tháng trượt: đáy 57,665 (11/2021), đỉnh 177,904 (07/2023), 118,368 trong năm 2024, 112,390 trong năm 2025, 92,709 tính đến 09/2026. Đây là **dòng visa được cấp**, không phải số sinh viên đang ở Sydney.
- **File SA4 của Bộ Giáo dục:** một snapshot (YTD 12/2025), 58 ô bị ẩn vì dưới 5. Đây là nơi học, không phải nơi ở.

---

## 4. Thiết kế phân tích

### 4.1 Phạm vi và đơn vị
- Dữ liệu chính: NSW Rental Bond Lodgements, 2018 (một năm) và 01/2021 đến 09/2026. Mỗi dòng là một bond mới (ngày, postcode, loại nhà, số phòng ngủ, rent tuần).
- Làm sạch: bỏ mã loại nhà ngoài F/H/T/O/U, rent ngoài $100-$5,000, số phòng ngủ thiếu hoặc ngoài 0-8. Lọc Greater Sydney bằng bảng quy đổi POA sang GCCSA của ABS (tỷ lệ ≥0.5, 257 postcode).
- Phân khúc chính: studio/1BR flat và 2BR flat. Các phân khúc khác để so sánh.

### 4.2 Exposure
| Phiên bản | Định nghĩa | Vai trò |
|---|---|---|
| E1 | Tỷ trọng enrolment theo SA4 (file DoE) | Chỉ để kiểm chứng, vì thực tế chỉ có 3 mức |
| E2 | Enrolment HE của SA4 phân bổ về các campus trong SA4 theo số khóa-địa điểm HE của CRICOS, rồi giảm theo khoảng cách | Chính, là **mô hình** |
| E3 | Khoảng cách từ postcode đến campus HE gần nhất | Chính, đơn giản |

- Chỉ dùng khóa HE cho E2 và E3 vì chính sách phân bổ 2026 áp dụng cho đại học công lập. Khi so với E1 phải dùng cùng phạm vi sector.
- Không dùng `Institution Capacity` của CRICOS làm trọng số: tổng capacity của các provider ở Greater Sydney là 832,877, trong khi enrolment NSW chỉ 387,611.

### 4.3 Bốn pha thời gian (từ BP0015, NSW)
1. **Đóng cửa:** đến 11/2021.
2. **Phục hồi:** 11/2021 đến 07/2023.
3. **Điều chỉnh:** 07/2023 đến giữa 2024.
4. **Đi ngang và giảm tiếp:** giữa 2024 đến 09/2026 (giảm rõ hơn trong 2026).

Cần đối chiếu thêm với chuỗi số sinh viên đang ở Úc theo tháng của Bộ Giáo dục (chưa parse), vì stock chậm hơn dòng visa.

### 4.4 Mô hình
- Hồi quy hedonic cho log rent: fixed effects theo postcode, quý, loại nhà × số phòng ngủ.
- Hệ số exposure × pha, sai số chuẩn theo SA3 bằng wild bootstrap.
- So sánh: các postcode trong Greater Sydney có tỷ lệ flat tương tự và rent nền 2018 tương tự, nhưng xa campus.
- Kiểm soát: số căn đề xuất trong DA theo postcode-năm; Airbnb (snapshot 2026, chỉ dùng như biến cắt ngang).

### 4.5 Báo cáo
- Chênh lệch tăng trưởng giữa hai mức exposure cụ thể (điểm phần trăm), khoảng bất định và quy ra AUD/tuần tại một mức rent tham chiếu.
- Không dùng "% rent mỗi 100,000 sinh viên".

---

## 5. Metrics

| Metric | Ý nghĩa với persona |
|---|---|
| M1. Chỉ số rent hợp đồng mới đã hiệu chỉnh, theo hành lang và phân khúc (AUD/tuần và chỉ số) | Rent flat ở từng hành lang diễn biến thế nào |
| M2. Exposure E2/E3 | Khu nào gắn với campus nhiều hơn (là mô hình) |
| M3. Chênh lệch tăng trưởng theo pha, exposure cao so với thấp | Có khác biệt không, bao nhiêu |
| M4. Studio/1BR so với 2BR, và postcode đối chứng không có campus | Tín hiệu có đặc trưng cho flat nhỏ gần campus không |
| M5. Điểm ổn định | Tỷ lệ kiểm tra độ bền giữ nguyên dấu và ít nhất nửa độ lớn |
| M6. Mức đủ dữ liệu | Số bond tối thiểu theo ô; cảnh báo nếu mỏng |
| M7. Bối cảnh cung | Số căn đề xuất trong DA (chưa phải nhà hoàn thành) |

---

## 6. Độ bền và phân loại bằng chứng (quy tắc đặt trước)

**Kiểm tra độ bền:** E2 so với E3; HE chỉ so với tất cả sector; bỏ từng hành lang (CBD, Ultimo, Redfern/Camperdown, Kensington, Parramatta, Macquarie); cửa sổ độ trễ 0/3/6 tháng giữa dòng visa và rent; ô mỏng bị loại; có và không có baseline 2018; postcode có/không bị chia giữa hai SA4.

**Phân loại:**
- **A, tín hiệu nhất quán:** dấu giống nhau và khoảng bất định không chứa 0 ở ít nhất hai pha; ít nhất 80% kiểm tra giữ dấu; không bị đảo khi bỏ một hành lang.
- **B, tín hiệu có điều kiện:** dấu ổn định nhưng khoảng bất định chứa 0, hoặc phụ thuộc vào một hành lang.
- **C, chưa phân biệt được với xu hướng chung:** các trường hợp còn lại.

Đặt quy tắc trước khi xem kết quả để tránh chọn cách đo cho đẹp.

---

## 7. Dataset

| Dataset | Trạng thái | Vai trò | Giới hạn |
|---|---|---|---|
| NSW Rental Bond 2021-2026 | Đã tải 62 file (79 MB), schema nhất quán, 1,883,402 dòng trong bộ phân tích | Kết quả chính | Chỉ hợp đồng mới; postcode; không có người thuê |
| NSW Rental Bond 2018 | Đã tải 331,880 dòng, từ bản sao UAT của data.nsw | Baseline trước COVID | Nguồn UAT cần xác nhận; thiếu 2019-2020 |
| ABS bảng quy đổi POA sang GCCSA/SA4/LGA | Đã tải, có tỷ lệ phân bổ | Địa lý | Postcode là xấp xỉ thống kê |
| CRICOS (Locations, Courses, Course Locations, Institutions) | Đã tải; ghép 100% theo (mã provider, tên địa điểm) | Vị trí campus, mức học | Không có số sinh viên; 861 dòng đã hết hạn cần loại |
| DoE SA4 enrolments | Đã tải, 1 snapshot | E1 | Nơi học; một năm; ô <5 bị ẩn |
| BP0015 visa granted | Đã parse cache | Pha thời gian | Dòng visa, bang đăng ký provider |
| NSW DA API | Đã gọi thử, không cần key; 3,900 DA tháng 3/2026 | Bối cảnh cung | `NumberOfNewDwellings` chỉ có ở 54%; không có loại "student accommodation" |
| Inside Airbnb Sydney | Đã kiểm tra: 20,833 listing (scrape 2026-09-17), calendar chỉ cho năm tới | Biến cắt ngang | Dùng tên LGA cũ; không có lịch sử |
| Valuer General (giá bán) | **Loại**: Cloudflare chặn truy cập tự động; giấy phép CC BY-NC-ND | Không | |

Chưa có: tọa độ postcode (ABS POA boundary), chuỗi stock sinh viên theo tháng của DoE, dân số/hộ thuê theo SA2.

---

## 8. Điều dự án không kết luận

- Du học sinh gây ra bao nhiêu phần trăm mức tăng rent của Sydney.
- Cắt X sinh viên thì rent giảm Y.
- Sinh viên sống ở đâu (exposure đo nơi học, không phải nơi ở).
- Cần xây bao nhiêu giường.
- Khả năng chi trả (không có thu nhập hộ).

---

## 9. Việc còn mở và rủi ro

1. ~~Tải ranh giới POA của ABS~~ Đã xong: centroid, bảng exposure E1/E2/E3 và panel nằm trong `processed/` (xem `DATA_README.md`). Khoảng cách tính từ centroid postcode nên độ phân giải khoảng 1 km.
2. Xác nhận nguồn 2018 (UAT) và tìm 2019-2020; nếu không có, giới hạn kết luận về baseline.
3. ~~9 postcode không khớp SA4~~ Đã xử lý: đó là 10 postcode Central Coast (ABS tính vào Greater Sydney), loại khỏi pool phân tích còn 247 postcode.
4. Xác nhận persona với một người thực tế, và tìm tài liệu 2025-2026 của council.
5. Tính trước mức chênh lệch tối thiểu phát hiện được ở cấp postcode-quý.
6. Phương án dự phòng nếu không tìm được hành lang nào có biến thiên đủ: chuyển sản phẩm thành bảng theo dõi mô tả rent flat theo hành lang, ghi rõ mức bằng chứng C.
