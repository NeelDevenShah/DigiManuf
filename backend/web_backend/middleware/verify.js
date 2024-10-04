const jwt = require('jsonwebtoken')
const JWT_SECRET = process.env.SECRET_KEY;


const verifyuser = async(req, res, next) => {
    console.log("cookie", req.cookies)
    const token = await req.cookies.token;
    console.log(token)
    if (!token) {
        return res.sendStatus(401).json({ error: "Unauthorized" })
    }
    
    try {
        const data = jwt.verify(token, JWT_SECRET);
        req.user = await data.user;
        next();
    } catch (error) {
        res.status(401).sendStatus("Please authenticate using a valid token");
    }
}

module.exports = verifyuser

