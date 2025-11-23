<?php
class A {
    public $x;
    function __destruct() {
        system($this->x);
    }
}
?>
