extern crate nifpga_dll;

use pyo3::prelude::*;
use pyo3::types::IntoPyDict;
use std::thread;
use std::time::Duration;
use std::sync::{Arc, Mutex};
use crossbeam;
use nifpga_dll::Session;


#[derive(Clone)]
#[pyclass]
struct Configuration {
    bit_file: String,
    signature: String,
    ni_address: String,
    run: bool,
    close_on_reset: bool,
    fifo: u32,
    dma_buffer_size: usize,
    fifo_reading_buffer: usize,
    min_packet: usize,
    delay_us: u64,
    debug: bool
}

fn fpga_loop(conf: &Configuration, tx: &crossbeam::channel::Sender<Vec<u64>>, stop_event: Arc<Mutex<bool>>) {

    let session = Session::open(
        conf.bit_file.as_str(),
        conf.signature.as_str(), //signature from generated header
        conf.ni_address.as_str(),
        conf.run, //run on open
        conf.close_on_reset //close_on_reset on close
    ).unwrap();

    let (reader, depth) = session.open_read_fifo::<u64>(conf.fifo, conf.dma_buffer_size).unwrap();

    println!("Actual DMA FIFO  {} set depth: {} actual depth: {}", conf.fifo, conf.dma_buffer_size, depth);
    println!("conf.fifo_reading_buffer: {}", conf.fifo_reading_buffer);
    println!("debug: {}", conf.debug);

    let mut read_buff:Vec<u64> = Vec::with_capacity(conf.fifo_reading_buffer);
    read_buff.resize(conf.fifo_reading_buffer, 0);

    let mut read_buff_zero_size:Vec<u64> = Vec::with_capacity(0);
    let mut data_available=0;

    let debug = conf.debug;
    // let debug = false;

    // let mut now_time = Instant::now();

    *stop_event.lock().unwrap() = false;

    loop {
        if *stop_event.lock().unwrap() {
            break;
        }

        // let last_time = Instant::now();
        if data_available==0 {
            
            if conf.delay_us>0 {std::thread::sleep(Duration::from_micros(conf.delay_us)); };
            data_available = (reader.read(&mut read_buff_zero_size, 0).unwrap() / conf.min_packet)*conf.min_packet;

            if debug==true {
                if (data_available) > 0 {
                        println!("data_available was 0 now :{}", data_available);
                }
            }

        }

        if data_available>0 {

            if debug==true {
                if (data_available) > 0 {
                        println!("data_available was > 0 now :{}", data_available);
                }
            }

            read_buff.resize((data_available / conf.min_packet)*conf.min_packet, 0);

            let len_data:usize = reader.read(&mut read_buff, conf.fifo_reading_buffer as u32).unwrap();

            if debug==true {
                if (data_available) > 0 {
                        println!("len_data:{}", data_available);
                }
            }

            data_available = (len_data / conf.min_packet)*conf.min_packet;

            if debug==true {
                if (data_available) > 0 {
                        println!("data_available before rounding:{}", data_available);
                }
            }

            if read_buff.len()>0 {
                tx.send(read_buff.to_vec()).unwrap();
                if debug==true {
                    println!("len_data {}", len_data);
                }
            }

        }

        // now_time = Instant::now();
        // let delta_time
        //     = now_time - last_time;

    }

}

/// Reading out from NI FPGA FIFOs with a separate thread allowing fast data-rate in Python.
///
/// It is implemented in Rust and it provides in Python the handle to start a separate thread running
/// a continuously polling loop, store the received data in a queue and reading them asynchronously.
/// This allow to receive data from nifpga in Python without loosing data even for fast data-rate.
///
#[pymodule]
fn nifpga_fast_fifo_recv(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_class::<NifpgaFastFifoRecv>()?;
    Ok(())
}

#[pyclass]
struct NifpgaFastFifoRecv {
    conf: Configuration,
    tx: crossbeam::channel::Sender<Vec<u64>>,
    rx: crossbeam::channel::Receiver<Vec<u64>>,
    thread_handle: Option<std::thread::JoinHandle<()>>,
    stop_event: Arc<Mutex<bool>>,
}

///provaC
#[pymethods]
impl NifpgaFastFifoRecv {
    ///Create a new NifpgaFastFifoRecv
    ///NifpgaFastFifoRecv(bitfile, signature, run, close_on_reset, fifo, dma_buffer_size,
    ///fifo_reading_buffer, fifo_buffer_size)
    #[new]
    #[pyo3(signature = (bitfile = "X", signature = "ABCD12345678", ni_address = "RI0", run = false, close_on_reset = false, fifo = 0, dma_buffer_size=50000, fifo_reading_buffer=10000, min_packet=1, delay_us = 0, debug = false))]
    fn new(bitfile: &str,
           signature: &str,
           ni_address:  &str,
           run: bool,
           close_on_reset: bool,
           fifo: u32,
           dma_buffer_size: usize,
           fifo_reading_buffer: usize,
           min_packet: usize,
           delay_us: u64,
           debug: bool) -> Self {

        let (tx, rx) = crossbeam::channel::unbounded();
        NifpgaFastFifoRecv { conf: Configuration{bit_file:String::from(bitfile),
                                                 signature:String::from(signature),
                                                 ni_address:String::from(ni_address),
                                                 run,
                                                 close_on_reset,
                                                 fifo,
                                                 dma_buffer_size,
                                                 fifo_reading_buffer,
                                                 min_packet,
                                                 delay_us,
                                                 debug},
                  tx: tx,
                  rx: rx,
                  thread_handle: None::<std::thread::JoinHandle<()>>,
                  stop_event: Arc::new(Mutex::new(false)),
        }
    }

    ///thread_start run the thread
    fn thread_start(&mut self, _py: Python) -> PyResult<()> {
        println!("Start two threads.");
        let conf_local = self.conf.clone();
        let tx_local = self.tx.clone();
        let stop_event = self.stop_event.clone();


        match &self.thread_handle {
            Some(_x)=>{
                eprintln!("THREAD ALREADY EXITS")
            },
            None=>{
                let handle = thread::spawn(move || {
                //fpga_loop_dummy(&conf_local, &tx_local, stop_event);
                fpga_loop(&conf_local, &tx_local, stop_event)
                });

                println!("Thread started!");

                self.thread_handle = Some(handle);


            },
        };

        Ok(())
    }

    ///thread_is_running return true is thread is running
    fn thread_is_running(&mut self, py: Python) -> PyResult<PyObject> {
        let status = match &self.thread_handle {
            Some(_x)=>{
                true
            },
            None=>{
                false
            },
        };
        Ok(status.to_object(py).into())
    }

    ///thread_stop stop the thread
    fn thread_stop(&mut self, _py: Python) -> PyResult<()> {
        *self.stop_event.lock().unwrap() = true;
        println!("stop_event True");

        if let Some(handle) = self.thread_handle.take() {
           handle.join().expect("failed to join thread");
        }
        else {
            eprintln!("THREAD DO NOT EXITS");
        }

        self.thread_handle = None::<std::thread::JoinHandle<()>>;

        // match th {
        println!("stop_event True done");
        Ok(())
    }

    ///get data from the internal queue
    fn get_data(&mut self, py: Python) -> PyResult<PyObject> {
        let empty_vec:Vec<u64> = Vec::new();
        let debug = self.conf.debug;

        if debug==true {
            if self.rx.len() > 0 {
                println!("self.rx.len() {}", self.rx.len());
            }
        }

        let vec_all_rx: Vec<Vec<u64>> = self.rx.try_iter().collect();

        if vec_all_rx.len()>0 {
            let vec_joined:Vec<u64> = vec_all_rx.into_iter().flatten().collect();
            if debug==true {
                println!("vec_joined.len() = {}", vec_joined.len());
            }
            //send to Python an array object
            Ok(vec_joined.to_object(py).into())
        }
        else
        {
            //send to Python an empty object
            Ok(empty_vec.to_object(py).into())
        }

    }

    ///get the current configuration
    fn get_conf(&mut self, py: Python) -> PyResult<PyObject> {
        let vect_for_dict: Vec<(&str, PyObject)> = vec![
            ("bit_file", self.conf.bit_file.to_object(py)),
            ("signature", self.conf.signature.to_object(py)),
            ("ni_address", self.conf.ni_address.to_object(py)),
            ("run", self.conf.run.to_object(py)),
            ("close_on_reset", self.conf.close_on_reset.to_object(py)),
            ("fifo", self.conf.fifo.to_object(py)),
            // ("port", self.conf.port.to_object(py)),
            ("dma_buffer_size", self.conf.dma_buffer_size.to_object(py)),
            ("fifo_reading_buffer", self.conf.fifo_reading_buffer.to_object(py)),
            ("delay_us", self.conf.delay_us.to_object(py)),
            ("min_packet", self.conf.min_packet.to_object(py))
        ];
        let d = vect_for_dict.into_py_dict(py);
        Ok(d.into())
    }


}


