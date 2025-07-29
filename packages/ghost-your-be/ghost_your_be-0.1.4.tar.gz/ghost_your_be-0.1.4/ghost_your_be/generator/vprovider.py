from faker.providers import BaseProvider
import random
import unicodedata
import string

class VietnamProvider(BaseProvider):
    
    def vietnam_phone(self):
        return "+84" + self.numerify(" 9## ### ###")
    
    def vietnam_name(self):
        first_names = ["Anh", "An", "Bảo", "Bình", "Cường", "Dũng", "Duy", "Đạt", "Đức", "Hiếu",
    "Hoàng", "Hùng", "Huy", "Khoa", "Khánh", "Lâm", "Long", "Minh", "Nam", "Nghĩa",
    "Phong", "Phúc", "Quân", "Quang", "Sơn", "Thành", "Thiện", "Thịnh", "Tú", "Tuấn",
    "Tùng", "Việt", "Vũ", "Xuân", "Tài", "Tâm", "Thắng", "Tiến", "Trung", "Trường",
    "Hải", "Hào", "Hiệp", "Linh", "Mạnh", "Ngọc", "Nhân", "Phương", "Thanh", "Toàn",
    "Chi", "Dung", "Hà", "Hạnh", "Hiền", "Hoa", "Hồng", "Huệ", "Hương", "Lan",
    "Liên", "Loan", "Mai", "My", "Nga", "Ngân", "Nhung", "Nhi", "Như", "Oanh",
    "Phương", "Quyên", "Thảo", "Thi", "Thu", "Thúy", "Thủy", "Tiên", "Trang", "Trinh",
    "Tuyết", "Vân", "Yến", "Xuân", "Châu", "Diệp", "Diễm", "Giang", "Hằng", "Kim",
    "Khánh", "Linh", "Ly", "Mỹ", "Ngọc", "Quỳnh", "Thanh", "Thơ", "Trâm", "Uyên"]
        middle_names = ["Thị", "Văn", "Đức", "Thế", "Thái", "Quốc", "Ngọc", "Thành", "Hữu", "Trọng",]
        last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Trịnh", "Đào", "Đoàn",
    "Vương", "Trương", "Tạ", "Lưu", "Lương", "Mai", "Cao", "Thái", "Châu", "Tô",
    "Tăng", "Hà", "Quách", "Tôn", "Mạc", "Lâm", "Thạch", "Diệp", "Phùng", "Tống",
    "Kiều", "Liêu", "Lã", "Hứa", "La", "Thân", "Triệu", "Trang", "Nhữ", "Tôn Nữ",
    "Tiêu", "Doãn", "Chu", "Diêm", "Vi", "Khúc", "Tạ", "Giang", "Bạch", "Từ",
    "Âu", "Hàn", "Thẩm", "Thập", "Ninh", "Lục", "Chế", "Khổng", "Thủy", "Tất",
    "Khuất", "Mã", "Từ", "Chung", "Thái", "Tăng", "Sơn", "Kim", "Kha", "Tiêu",
    "Lục", "Hàn", "Đường", "Ông", "An", "Bành", "Nhâm", "Cù", "Nghiêm", "Kỳ",
    "Lại", "Phó", "Ân", "Danh", "Dư", "Tăng", "Thiều", "Văn"]
        return f"{self.random_element(last_names)} {self.random_element(middle_names)} {self.random_element(first_names)}"
    
    def vietnam_address(self):
        provinces = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
    "Huế", "Nha Trang", "Đà Lạt", "Vũng Tàu", "Buôn Ma Thuột",
    "Vinh", "Hạ Long", "Phan Thiết", "Quy Nhơn", "Pleiku",
    "Thái Nguyên", "Biên Hòa", "Long Xuyên", "Rạch Giá", "Mỹ Tho",
    "Tuy Hòa", "Hà Tiên", "Bắc Ninh", "Thái Bình", "Nam Định"]
        street_address = ["Lê Lợi", "Nguyễn Huệ", "Trần Hưng Đạo", "Hai Bà Trưng", "Nguyễn Thị Minh Khai",
    "Lê Duẩn", "Điện Biên Phủ", "Cách Mạng Tháng Tám", "Phạm Ngũ Lão", "Nguyễn Văn Linh",
    "Lê Hồng Phong", "Nguyễn Trãi", "Lý Thường Kiệt", "Phan Đình Phùng", "Võ Văn Tần",
    "Bà Triệu", "Nguyễn Du", "Pasteur", "Tôn Đức Thắng", "3 Tháng 2",
    "Nguyễn Đình Chiểu", "Cao Thắng", "Phan Chu Trinh", "Hùng Vương", "Nguyễn Khuyến", "Quận 1", "Quận 2", "Quận 3", "Quận 4", "Quận 5", "Quận 6", "Quận 7", "Quận 8", "Quận 9", "Quận 10", "Quận 11", "Quận 12"]
        address = f"{self.random_element(street_address)}, {self.random_element(provinces)}"
        return address
    
    def vietnam_id(self):
        return self.numerify("0###########")
    
    def vietnam_email(self):
        name = self.vietnam_name().lower().replace(" ", "").replace(".", "")
        name = ''.join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "gmail.vn", "yahoo.vn", "hotmail.vn", "outlook.vn"]
        return f"{name}@{self.random_element(domains)}"
    
    def vietnam_motorcycle(self):
        motorcycles = ["Honda Wave Alpha", "Honda Vision", "Yamaha Exciter", "Yamaha Sirius", "Suzuki Raider", "Suzuki Impulse", "SYM Attila", "SYM Elite", "Piaggio Liberty", "Piaggio Vespa"]
        return self.random_element(motorcycles)
    
    def vietnam_car(self):
        cars = ["Toyota Camry", "Toyota Corolla", "Toyota Fortuner", "Toyota Hilux", "Toyota Innova", "Toyota Land Cruiser", "Toyota Prado", "Toyota Vios"]
        return self.random_element(cars)
    
    def vietnam_year(self):
        return self.random_int(min=1900, max=2050)
    
    def vietnam_month(self):
        return self.random_int(min=1, max=12)
    
    def vietnam_day(self):
        return self.random_int(min=1, max=31)
    
    def vietnam_date(self):
        date = f"{self.vietnam_year()}-{self.vietnam_month()}-{self.vietnam_day()}"
        if self.vietnam_month() == 2:
            if self.vietnam_year() % 4 == 0 and (self.vietnam_year() % 100 != 0 or self.vietnam_year() % 400 == 0):
                if self.vietnam_day() > 29:
                    date = f"{self.vietnam_year()}-{self.vietnam_month()}-29"
            else:
                if self.vietnam_day() > 28:
                    date = f"{self.vietnam_year()}-{self.vietnam_month()}-28"
        elif self.vietnam_month() in [4, 6, 9, 11]:
            if self.vietnam_day() > 30:
                date = f"{self.vietnam_year()}-{self.vietnam_month()}-30"
        return date
    
    def vietnam_time(self):
        return f"{self.random_int(min=0, max=23)}:{self.random_int(min=0, max=59)}:{self.random_int(min=0, max=59)}"
    
    def vietnam_password(self):
        return self.random_element(string.ascii_letters + string.digits)

    def vietnam_username(self):
        return self.random_element(string.ascii_letters + string.digits)
    
    def vietnam_age(self):
        return self.random_int(min=1, max=100)
    
    def vietnam_gender(self):
        return self.random_element(["male", "female"])
    
    def vietnam_job(self):
        jobs = ["Developer", "Designer", "Manager", "Sales", "Marketing", "HR", "Accountant", "Customer Service", "IT Support", "Data Analyst"]
        return self.random_element(jobs)
    
    def vietnam_salary(self):
        return self.random_int(min=1000000, max=10000000)
    
    def vietnam_company(self):
        types = ["IT", "Marketing", "Sales", "HR", "Accounting", "Customer Service", "IT Support", "Data Analyst"]
        names = ["FPT", "Viettel", "VNPT", "Vietcombank", "BIDV", "Vinamilk", "TH True Milk", "Masan Group", "Sabeco", "Habeco", 
    "Trung Nguyên Legend", "Acecook Việt Nam", "Kinh Đô", "Nutifood", "Vissan", "Coteccons", "Viglacera",  "Vinfast", "Thaco Group", "Greenfeed Vietnam", "Masan MEATLife", "Tôn Hoa Sen", "Vietnam Airlines", "Bamboo Airways", "Saigontourist", "Vinpearl", "Muong Thanh Hospitality", 
    "The Coffee House", "Highlands Coffee", "Pizza 4P's", "Golden Gate Group", "BHD Star Cineplex"]
        company = [f"{self.random_element(types)} {self.random_element(names)}" for _ in range(10)]
        return company
    
    def vietnam_school(self):
        types = ["THPT", "THCS", "Đại học", "Cao đẳng", "Trung cấp", "Học viện", "Mầm non", "Tiểu học"]
        name = ["FPT", "Báck Khoa", "Kinh Tế Quốc Dân", "Thương Mại", "Ngoại Thương", "Báo Chí", "Thuỷ Lợi", "Ngoại Giao"]
        school = [f"{self.random_element(types)} {self.random_element(name)}" for _ in range(10)]
        return school