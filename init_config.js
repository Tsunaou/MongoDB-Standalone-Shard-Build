rs.initiate(
    {
        _id: "config",
        configsvr: true,
        members: [
            { _id : 0, host : "114.212.84.175:29010" },
            { _id : 1, host : "114.212.84.175:29011" },
            { _id : 2, host : "114.212.84.175:29012" }
        ]
    }
);
rs.status();
