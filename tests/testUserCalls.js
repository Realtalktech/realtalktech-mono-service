const DEFAULT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDc4MDM2ODcsImlhdCI6MTcwNzc5Mjg4Nywic3ViIjo1fQ.OuGM28dMenfX3hUUctfVR_-6kAb9FYPIRvyYtCeu-c0';

// User -------------------------------------

const fetchUser = (username, token = DEFAULT_TOKEN) => {
  const url = `http://ec2-3-95-180-146.compute-1.amazonaws.com/user/${username}`
  const params = {
    method: "GET",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  }
  fetch(url, params).then(res => {
    return res.text()
  }).then(json => {
    console.log("GOOD-fetchUser", json)
    // dispatch({type: "POSTS_SUCCESS", payload: json})
  }).catch((err) => {
    console.log("ERR-fetchUser", err)
  })
}
fetchUser('msmith21')

const endorseUser = (body, token = DEFAULT_TOKEN) => {
  const url = `http://ec2-3-95-180-146.compute-1.amazonaws.com/endorseUser`
  const params = {
    method: "PUT",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body)
  }
  fetch(url, params).then(res => {
    return res.json()
    // return res.text()
  }).then(json => {
    console.log("GOOD-endorseUser", json)
    // dispatch({type: "POSTS_SUCCESS", payload: json})
  }).catch((err) => {
    console.log("ERR-endorseUser", err)
  })
}

const bodyEndorse = {
  endorserUserId: 1,
  endorseeUsername: 2,
  vendorId: 5,
}
endorseUser(bodyEndorse)