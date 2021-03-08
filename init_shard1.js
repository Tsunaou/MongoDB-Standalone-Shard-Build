rs.initiate(
    {
        _id : "shard1",
        members: [
            { _id : 0, host : "114.212.84.175:27010" ,priority : 2 },
            { _id : 1, host : "114.212.84.175:27011" ,priority : 1 },
            { _id : 2, host : "114.212.84.175:27012" ,arbiterOnly :true }
        ]
    }
)
rs.status();