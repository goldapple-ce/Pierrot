import axios from "axios";

const baseUrl = "http://localhost:3001";

const urls = {
  login: `${baseUrl}/auth/login`,
  register: `${baseUrl}/auth/signup`,
  logout: `${baseUrl}/auth/logout`,
  auth: `${baseUrl}/auth/auth`,
  uploadVideo: `${baseUrl}/video/uploadVideo`,
};
// winer: 누가 이겼는지(이름String), opponent: 누구랑 쳤는지(이름String), date: 언제 쳤는지(Date), score: 몇대몇('00:00')

export const uploadVideo = async (winer, opponent, date, score) => {
  try {
    const result = await axios.post(
      urls.uploadVideo,
      {
        winer: winer,
        opponent: opponent,
        date: date,
        score: score,
      },
      { withCredentials: true }
    );
    return result.data;
  } catch (e) {
    console.log("error", e);
  }
};

export const login = async (email, password) => {
  try {
    const result = await axios.post(
      urls.login,
      {
        email: email,
        password: password,
      },
      { withCredentials: true }
    );
    return result.data;
  } catch (e) {
    console.log("error", e);
  }
};

export const signup = async (email, password, username, age) => {
  console.log("register");
  try {
    const result = await axios.post(
      urls.register,
      {
        email: email,
        passwd: password,
        name: username,
        age: age,
      },
      { withCredentials: true }
    );
    return result.data;
  } catch (e) {
    console.log("error", e);
  }
};

export const auth = async () => {
  try {
    const result = await axios.get(urls.auth, { withCredentials: true });
    return result.data;
  } catch (e) {
    console.log("error", e);
  }
};

export const logout = async () => {
  try {
    const reuslt = await axios.get(urls.logout, { withCredentials: true });
    return reuslt.data;
  } catch (e) {
    console.log("err", e);
  }
};
