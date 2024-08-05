const jwt = require('jsonwebtoken')
const JWT_SECRET = (process.env.JWT_SECRET || "This_is_the_secret@auth_key");
const cookieParser = require('cookie-parser');


const verifyuser = async(req, res, next) => {
    // console.log(req.cookies)
    const token = await req.cookies.token;
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

