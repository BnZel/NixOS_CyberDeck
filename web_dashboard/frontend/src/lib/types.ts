export interface GPS {
    datetime:string;
    longitude:number;
    longitude_direction:string;
    latitude:number;
    latitude_direction:string;
}

export interface Baro {
    datetime:string;
    temperature_c:number;
    pressure_hpa:number;
    altitude_m:number;
}

export interface CPU {
    datetime:string;
    temperature_c:number;
    cpu_load:number;
    memory_usage_mb:number;
    memory_usage_percent:number;
}

export interface Glove {
    A4:number;
}