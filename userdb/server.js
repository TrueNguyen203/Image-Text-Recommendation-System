const jsonServer = require('json-server')
const auth = require('json-server-auth')
const path = require('path')

const app = jsonServer.create()
const router = jsonServer.router(path.join(__dirname, 'db.json'))
const middlewares = jsonServer.defaults()

// /!\ Cần bind router db với app
app.db = router.db

const rules = auth.rewriter({
    // Quy tắc phân quyền
    users: 600, // Chỉ người dùng đã xác thực mới có thể truy cập danh sách users
})

// Áp dụng các middleware theo thứ tự sau
app.use(middlewares)
app.use(jsonServer.bodyParser)

// Middleware log để kiểm tra dữ liệu gửi lên từ Client
app.use((req, res, next) => {
    console.log(`[${req.method}] ${req.url}`, req.body)
    next()
})

// Tạo route đăng xuất (Logout) giả lập
app.post('/logout', (req, res) => {
    res.json({ message: 'Đăng xuất thành công' })
})

app.use(rules)
app.use(auth)
app.use(router)
app.listen(3000, () => {
    console.log('JSON Server with auth is running on http://localhost:3000')
})